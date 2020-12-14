import os
from typing import List, Tuple

from .tag import Tag
from .audio_file import AudioFile, ClutterFile
from .os_utils import (
    is_audio_file,
    create_dir,
    move_file,
    remove_directory
)
from .logger import log, warning


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
    if len(audio_files) > 0:
        for tag in Tag:
            candidate = audio_files[0].tags[tag]
            if all([
                audio_file.tags[tag] == candidate
                for audio_file in audio_files[1:]
            ]):
                for clutter_file in clutter_files:
                    clutter_file.tags[tag] = candidate

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
            clutter_files.append(ClutterFile(child_dir))
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
                    log(f'Discarded file: {file}')
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
        associate_clutter(
            nodes,
            ordering,
            clutter_file
        )


def associate_clutter(
    nodes: List[TreeNode],
    ordering: List[Tag],
    clutter_file: ClutterFile
):
    '''
    Given the tree-structured audio files, and a clutter file, assigns each
    clutter file to its associated node.

    Args:
        nodes (List[TreeNode]): List of nodes of the tree
        ordering (List[Tag]): List of tags along which the tree is ordered
        clutter_file (ClutterFile): File that must be sorted into the given
            nodes
    '''

    order_tag = ordering[0]

    try:
        tag_value = clutter_file.tags[order_tag]
    except KeyError:
        tag_value = f'Unknown {str(order_tag)}'

    for node in nodes:
        if node.name == tag_value:
            if (
                not node.children
                or
                len(ordering) == 1
            ):
                # Terminal node
                node.clutter_files.append(clutter_file)
            else:
                associate_clutter(
                    node.children,
                    ordering[1:],
                    clutter_file
                    )


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
    dry_run: bool
):
    '''
    Remove empty folders in the source directory.
    '''
    if not os.path.isdir(dir_src):
        return

    # remove empty subfolders
    files = os.listdir(dir_src)
    if len(files):
        for f in files:
            fullpath = os.path.join(dir_src, f)
            if os.path.isdir(fullpath):
                clean_up(fullpath, audio_files, dry_run)

    # if folder empty, delete it
    files = os.listdir(dir_src)
    if all([
        file in [
            audio_file.file
            for audio_file in audio_files
        ]
        for file in files
    ]):
        remove_directory(dir_src, dry_run, False)


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

    clean_up(dir_src, audio_files, dry_run)
