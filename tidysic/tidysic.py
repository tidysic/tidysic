import os
from typing import List, Tuple

from tidysic.tag import Tag
from tidysic.audio_file import AudioFile, ClutterFile
from tidysic.os_utils import (
    is_audio_file,
    create_dir,
    move_file,
    remove_directory
)
from tidysic.logger import log, warning


class TreeNode(object):
    '''
    Node of the tree-like structure used to sort audio files.

    Each TreeNode corresponds to a directory in the output of the program,
    this means that there is no single root node of the tree, but rather a
    list of first children.
    '''

    def __init__(self, name: str, tag: Tag):
        self._tag = tag
        self._name = name
        self._children = []
        self._clutter_files = []

    @property
    def tag(self) -> Tag:
        '''
        Tag type of the node's ordering level

        For instance, if a node's tag property is Tag.Artists,
        then everyone of its leaves will have this node's artist.
        '''
        return self._tag

    @property
    def name(self) -> str:
        '''
        Value of the tag with which this node was sorted.
        '''
        if self._name:
            return self._name
        else:
            return f'Unknown {str(self._tag)}'

    @property
    def children(self):
        '''
        Children nodes.
        '''
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def clutter_files(self):
        '''
        Non audio files (can also be directories) that should be placed in the
        same directory as self's children.

        All the files that were found in the same subdirectory of the input
        directory as all of self's leaves.
        '''
        return self._clutter_files

    def get_any_leaf(self) -> AudioFile:
        '''
        Returns a leaf of the tree whose root is `self`.
        '''
        for child in self.children:
            if isinstance(child, AudioFile):
                return child
            elif isinstance(child, TreeNode):
                leaf = child.get_any_leaf()
                if leaf is not None:
                    return leaf

    def build_name(self, format_string):
        '''
        Builds the name of the directory that will be created.
        '''
        file = self.get_any_leaf()
        if file:
            return file.fill_formatted_str(format_string)


def scan_folder(
    input_dir: str,
    guess: bool,
    dry_run: bool
) -> Tuple[List[AudioFile], List[ClutterFile]]:
    '''
    Parse the input folder, returning a flat list of AudioFiles.

    Returns an array of all the audio files found in the given directory and
    its children. This is were all tags guessing will happen.

    Args:
        input_dir (str): Whole path of the directory to scan
        guess (bool): Whether to apply guessing to untagged audio files
        dry_run (bool): Whether to apply eventual tag changes to files

    Returns:
        Tuple[List[AudioFile], List[ClutterFile]]: [description]
    '''
    files = [
        os.path.join(input_dir, file)
        for file in os.listdir(input_dir)
    ]

    child_dirs = [
        file
        for file in files
        if os.path.isdir(file)
    ]

    audio_files = [
        file
        for file in files
        if is_audio_file(file)
    ]

    clutter_files = [
        ClutterFile(file)
        for file in files
        if file not in child_dirs and file not in audio_files
    ]

    audio_files = [
        AudioFile(file)
        for file in audio_files
    ]
    if guess:
        for audio_file in audio_files:
            audio_file.guess_tags(dry_run)

    # Condition clutter
    common_tags = {}
    for tag in Tag:
        tag_value = None
        if len(audio_files) > 0:
            candidate = audio_files[0].tags[tag]
            if (
                candidate is not None
                and
                all([
                    audio_file.tags[tag] == candidate
                    for audio_file in audio_files[1:]
                ])
            ):
                tag_value = candidate

        common_tags[tag] = tag_value

    for clutter_file in clutter_files:
        clutter_file.tags = common_tags

    # Recursive step
    for child_dir in child_dirs:

        child_audio_files, child_clutter_files = scan_folder(
            child_dir,
            guess,
            dry_run
        )

        if len(child_audio_files) == 0:
            # No audio files in this child folder,
            # it is then considered as clutter
            clutter_dir = ClutterFile(child_dir)
            clutter_dir.tags = common_tags
            clutter_files.append(clutter_dir)
        else:
            audio_files += child_audio_files
            clutter_files += child_clutter_files

    return (audio_files, clutter_files)


def create_structure(
    audio_files: List[AudioFile],
    ordering: List[Tag],
    guess: bool,
    dry_run: bool
) -> list:
    '''
    Given a list of AudioFiles and an ordering,
    creates a list of either TreeNode objects or AudioFiles.
    '''

    if not ordering:
        # No tags for ordering given, we cannot sort the files
        return audio_files

    children = {}
    order_tag = ordering[0]

    # Sort files into a dictionary
    for file in audio_files:
        tag_value = file.tags[order_tag]
        if tag_value is None:
            if order_tag in [Tag.Artist, Tag.Title] and guess:
                file.guess_tags(dry_run)

                tag_value = file.tags[order_tag]

                if tag_value is None:
                    log(f'Discarded file: {file.file}')
            else:
                warning(f'''
File {file.file}
could not have its {str(order_tag)} tag determined.
It will move into an 'Unknown {str(order_tag)}' directory.\
                ''')

        if tag_value not in children:
            children[tag_value] = []
        children[tag_value].append(file)

    # Create nodes from dictionary
    child_nodes = []
    for tag_value, files in children.items():
        new_node = TreeNode(tag_value, order_tag)
        new_node.children = create_structure(
            files,
            ordering[1:],
            guess,
            dry_run
        )

        child_nodes.append(new_node)

    return child_nodes


def organize_clutter(
    nodes: List[TreeNode],
    ordering: List[Tag],
    clutter_files: List[ClutterFile]
):
    '''
    Given the tree-structured audio files, and the list of clutter files,
    assigns each clutter file to its associated node.

    Args:
        nodes (List[TreeNode]): List of nodes of the tree
        ordering (List[Tag]): List of tags along which the tree is ordered
        clutter_files (List[ClutterFile]): Files that must be sorted into the
            given nodes
    '''
    for clutter_file in clutter_files:
        if not associate_clutter(
            nodes,
            ordering,
            clutter_file
        ):
            clutter_files.remove(clutter_file)


def associate_clutter(
    nodes: List[TreeNode],
    ordering: List[Tag],
    clutter_file: ClutterFile
) -> bool:
    '''
    Given the tree-structured audio files, and a clutter file, assigns each
    clutter file to its associated node.

    Args:
        nodes (List[TreeNode]): List of nodes of the tree
        ordering (List[Tag]): List of tags along which the tree is ordered
        clutter_file (ClutterFile): File that must be sorted into the given
            nodes

    Returns:
        bool: True if the clutter was successfully associated
    '''

    order_tag = ordering[0]

    if order_tag in clutter_file.tags:
        tag_value = clutter_file.tags[order_tag]
        for node in nodes:
            if (
                tag_value is not None
                and
                node.name == tag_value
            ):
                #  The clutter is down the right path
                if (
                    not node.children
                    or
                    len(ordering) == 1
                    or
                    not associate_clutter(
                        node.children,
                        ordering[1:],
                        clutter_file
                    )
                ):
                    # Terminal node
                    node.clutter_files.append(clutter_file)
                return True

    return False


def move_files(
    nodes: list,
    dir_target: str,
    formats: List[str],
    with_clutter: bool,
    dry_run: bool,
    verbose: bool
):
    '''
    Moves the given files into a folder hierarchy following
    the given structure.

    Assumes the given TreeNode's children are also TreeNodes
    '''
    for node in nodes:

        if isinstance(node, AudioFile):
            # Leaf of the structure tree
            assert(len(formats) == 1)
            move_file(
                node.file,
                node.build_file_name(formats[0]),
                dir_target,
                dry_run,
                verbose
            )

        elif isinstance(node, TreeNode):

            # Recursive step
            assert(len(formats) > 0)
            sub_dir_target = create_dir(
                node.build_name(formats[0]),
                dir_target,
                dry_run,
                verbose
            )

            if with_clutter:
                for clutter_file in node.clutter_files:
                    move_file(
                        clutter_file.file,
                        clutter_file.name,
                        sub_dir_target,
                        dry_run,
                        verbose
                    )

            move_files(
                node.children,
                sub_dir_target,
                formats[1:],
                with_clutter,
                dry_run,
                verbose
            )


def clean_up(
    dir_src: str,
    audio_files: List[AudioFile],
    clutter_files: List[ClutterFile],
    dry_run: bool,
    verbose: bool
):
    '''
    Remove empty folders in the given directory.

    This method may seem needlessly convoluted, but it serves the purpose of
    actually notifying of directory removal even when `dry_run` is True.

    Returns true if the given folder was deleted.
    '''
    if not os.path.isdir(dir_src):
        return False

    # Recursive step
    files = [
        os.path.join(dir_src, filename)
        for filename in os.listdir(dir_src)
    ]

    for file in files:
        if clean_up(
            file,
            audio_files,
            clutter_files,
            dry_run,
            verbose
        ):
            files.remove(file)

    # We kept track of which files were moved for this reason:
    deleted_files = [
        file.file
        for file in audio_files + clutter_files
    ]
    # Vacuously true if dry_run wasn't specified
    if all([
        file in deleted_files
        for file in files
    ]):
        remove_directory(dir_src, dry_run, verbose)
        return True

    else:
        return False


def organize(
    dir_src: str,
    dir_target: str,
    with_album: bool,
    with_clutter: bool,
    guess: bool,
    dry_run: bool,
    verbose: bool
):
    '''
    Concisely runs the three parts of the algorithm.
    '''

    ordering = [Tag.Artist]
    if with_album:
        ordering += [Tag.Album]

    audio_files, clutter_files = scan_folder(
        dir_src,
        guess,
        dry_run
    )

    root_nodes = create_structure(
        audio_files,
        ordering,
        guess,
        dry_run
    )

    organize_clutter(
        root_nodes,
        ordering,
        clutter_files
    )

    formats = [
        '{{artist}}',
        '{({year}) }{{album}}',
        '{{track:02d}. }{{title}}'
    ]
    move_files(
        root_nodes,
        dir_target,
        formats,
        with_clutter,
        dry_run,
        verbose
    )

    clean_up(
        dir_src,
        audio_files,
        clutter_files,
        dry_run,
        verbose
    )
