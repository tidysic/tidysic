import os
from typing import List

from .tag import Tag
from .audio_file import AudioFile
from .os_utils import (
    create_dir,
    get_audio_files,
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

    @property
    def tag(self):
        '''
        Tag type of the node's ordering level

        For instance, if a node's tag property is Tag.Artists,
        everyone of its children's name will be artist names
        '''
        return self._tag

    @property
    def name(self):
        # TODO: Allow for formatting as well as leaves
        if self._name:
            return self._name
        else:
            return f'Unknown {str(self._tag)}'

    @property
    def children(self):
        '''Children nodes, ordered by name'''
        return self._children

    @children.setter
    def children(self, value):
        self._children = value


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
    order_tag = ordering.pop(0)

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
            ordering,
            guess,
            dry_run
        )

        child_nodes.append(new_node)

    return child_nodes


def move_files(
    nodes: list,
    dir_target: str,
    format: str,
    dry_run=False,
):
    '''
    Moves the given files into a folder hierarchy following
    the given structure.

    Assumes the given TreeNode's children are also TreeNodes
    '''
    for child in nodes:

        if isinstance(child, AudioFile):
            # Leaf of the structure tree
            move_file(
                child.file,
                child.build_file_name(format),
                dir_target,
                dry_run,
                False
            )

        elif isinstance(child, TreeNode):
            # Recursive step
            sub_dir_target = create_dir(
                child.name,
                dir_target,
                dry_run,
                False
            )

            move_files(
                child.children,
                sub_dir_target,
                format,
                dry_run
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
    guess: bool,
    dry_run: bool,
    verbose: bool
):
    '''
    Concisely runs the three parts of the algorithm.
    '''

    structure = [Tag.Artist]
    if with_album:
        structure += [Tag.Album]

    audio_files = get_audio_files(dir_src)

    root_nodes = create_structure(
        audio_files,
        structure,
        guess,
        dry_run
    )

    format = '{title}'
    move_files(
        root_nodes,
        dir_target,
        format,
        dry_run
    )

    clean_up(dir_src, audio_files, dry_run)
