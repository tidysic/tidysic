import os
from typing import Union, Sequence

from tidysic.tag import Tag
from tidysic.audio_file import AudioFile, ClutterFile
from tidysic.formatted_string import FormattedString
from tidysic.ordering import Ordering, OrderingStep
from tidysic.os_utils import (
    is_audio_file,
    create_dir,
    move_file,
    remove_file,
    remove_directory
)
from tidysic import logger


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
        self._children: list[Union['TreeNode', AudioFile]] = []
        self._clutter_files: list[ClutterFile] = []

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

        assert False, 'TreeNode has no child'

    def build_name(self, formatted_string: FormattedString):
        '''
        Builds the name of the directory that will be created.
        '''
        file = self.get_any_leaf()
        if file:
            return formatted_string.build(file.tags)


class Tidysic:

    def __init__(
        self,
        input_dir,
        output_dir,
        dry_run=False,
        interactive=False,
        verbose=False,
        with_clutter=False
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir

        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.with_clutter = with_clutter

        self.ordering = Ordering([
            OrderingStep(Tag.Artist, FormattedString('{{artist}}')),
            OrderingStep(Tag.Album, FormattedString('{({year}) }{{album}}')),
            OrderingStep(Tag.Title, FormattedString('{{track}. }{{title}}'))
        ])

        self.audio_files: list[AudioFile] = []
        self.clutter_files: list[ClutterFile] = []

        self.root_nodes: list[TreeNode] = []

    def organize(self):
        '''
        Concisely runs the whole algorithm.
        '''
        self.scan_folder()
        self.create_structure()
        self.move_files()
        self.clean_up()

    def scan_folder(self):
        '''
        Parse the input directory, collecting an array of AudioFiles and
        an array of ClutterFiles.
        '''
        self.audio_files, self.clutter_files = self._scan_folder(
            self.input_dir
        )

    def create_structure(self):
        '''
        Builds the tree-like structure of AudioFiles from the flat list.
        '''
        self.root_nodes = self._create_structure(
            self.audio_files,
            self.ordering
        )

        if self.with_clutter:
            
            associated_clutter = [
                clutter_file
                for clutter_file in self.clutter_files
                if self._associate_clutter(
                    self.root_nodes,
                    self.ordering,
                    clutter_file
                )
            ]

            discarded_clutter = set(self.clutter_files) - set(associated_clutter)
            if discarded_clutter:
                logger.warning(
                    ["Discarded the following non-audio files :"]
                    +
                    [
                        clutter.file
                        for clutter in discarded_clutter
                    ]
                )
            
            self.clutter_files = associated_clutter

    def move_files(self):
        '''
        Once the tree has been built, use this to move files from the input
        directory to the output directory.
        '''
        self._move_files(
            self.root_nodes,
            self.output_dir,
            self.ordering
        )

    def clean_up(self):
        '''
        Removes empty subdirectories left in the input directory after moving
        the files.
        '''
        self._clean_up(
            self.input_dir,
            self.audio_files,
            self.clutter_files
        )

    def _scan_folder(
        self,
        input_dir: str
    ) -> tuple[list[AudioFile], list[ClutterFile]]:
        '''
        Recursive method used in the public `scan_folder` method.

        Args:
            input_dir (str): Whole path of the directory to scan

        Returns:
            tuple[list[AudioFile], list[ClutterFile]]: AudioFiles and
                ClutterFiles found inside.
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
            AudioFile(file)
            for file in files
            if is_audio_file(file)
        ]

        clutter_files = [
            ClutterFile(file)
            for file in files
            if file not in child_dirs and not is_audio_file(file)
        ]

        # Find tags common to all audio files in the directory
        common_tags = {}
        for tag in Tag:
            tag_value = None
            if len(audio_files) > 0:
                candidate = audio_files[0].tags[tag]
                if all([
                        audio_file.tags[tag] == candidate
                        for audio_file in audio_files[1:]
                ]):
                    tag_value = candidate

            common_tags[tag] = tag_value

        for clutter_file in clutter_files:
            clutter_file.tags = common_tags

        # Recursive step
        for child_dir in child_dirs:

            child_audio_files, child_clutter_files = self._scan_folder(
                child_dir
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

    def _create_structure(
        self,
        audio_files: list[AudioFile],
        ordering: Ordering,
    ) -> Sequence[Union[TreeNode, AudioFile]]:
        '''
        Recursive method used in the public `create_structure` method.

        Creates all nodes or leaves of the tree with the given ordering.

        Args:
            audio_files (list[AudioFile]): Audio files to put in the tree.
            ordering (Ordering): Order of the tree.

        Returns:
            Sequence[Union[TreeNode, AudioFile]]: Children of depth one.
        '''
        assert ordering.steps, 'No ordering given'
        order_tag = ordering.steps[0].tag

        if order_tag == Tag.Title:
            return audio_files

        # Sort files into a dictionary
        children: dict[Tag, list[AudioFile]] = {}
        for file in audio_files:
            tag_value = file.tags[order_tag]
            if tag_value is None:
                if (
                    order_tag in {
                        ordering_step.tag
                        for ordering_step in ordering.steps
                    }
                    and
                    self.interactive
                ):
                    tag_value = file.ask_and_set_tag(order_tag)
                    if tag_value is None and self.verbose:
                        logger.log(f'Discarded file: {file.file}')

                elif self.verbose:
                    logger.warning(
                        f'File {file.file}\n'
                        f'could not have its {str(order_tag)} tag '
                        'determined.\n'
                        f'It will move into [blue]Unknown {str(order_tag)}'
                        'directory.'
                    )

            if tag_value not in children:
                children[tag_value] = []
            children[tag_value].append(file)

        # Create nodes from dictionary
        child_nodes = []
        for tag_value, files in children.items():
            new_node = TreeNode(tag_value, order_tag)
            new_node.children = self._create_structure(
                files,
                ordering.sub_ordering()
            )

            child_nodes.append(new_node)

        return child_nodes

    def _associate_clutter(
        self,
        nodes: list[TreeNode],
        ordering: Ordering,
        clutter_file: ClutterFile
    ) -> bool:
        '''
        Attempts to place the given ClutterFile into the tree-like structure.

        Args:
            nodes (list[TreeNode]): List of nodes of the tree
            ordering (list[Tag]): List of tags along which the tree is ordered
            clutter_file (ClutterFile): File that must be sorted into the given
                nodes

        Returns:
            bool: True if the clutter was successfully associated
        '''

        order_tag = ordering.steps[0].tag
        if order_tag in clutter_file.tags:
            tag_value = clutter_file.tags[order_tag]
            for node in nodes:
                if (
                    tag_value is not None
                    and
                    node.name == tag_value
                ):
                    if (
                        not node.children
                        or
                        len(ordering.steps) <= 2
                        or
                        not self._associate_clutter(
                            node.children,
                            ordering.sub_ordering(),
                            clutter_file
                        )
                    ):
                        # The clutter cannot descend further down
                        node.clutter_files.append(clutter_file)
                    return True

        return False

    def _move_files(
        self,
        nodes: list,
        dir_target: str,
        ordering: Ordering
    ):
        '''
        Moves the given files into a folder hierarchy following
        the given structure.
        '''
        for node in nodes:
            if isinstance(node, AudioFile):
                # Leaf of the structure tree
                assert ordering.is_terminal()

                node.save_tags(verbose=self.verbose, dry_run=self.dry_run)
                formatted_string = ordering.steps[0].format
                move_file(
                    node.file,
                    node.build_file_name(formatted_string),
                    dir_target,
                    self.dry_run,
                    self.verbose
                )

            elif isinstance(node, TreeNode):
                # Recursive step
                assert not ordering.is_terminal()
                formatted_string = ordering.steps[0].format
                sub_dir_target = create_dir(
                    node.build_name(formatted_string),
                    dir_target,
                    self.dry_run,
                    self.verbose
                )

                if self.with_clutter:
                    for clutter_file in node.clutter_files:
                        move_file(
                            clutter_file.file,
                            clutter_file.name,
                            sub_dir_target,
                            self.dry_run,
                            self.verbose
                        )

                self._move_files(
                    node.children,
                    sub_dir_target,
                    ordering.sub_ordering()
                )

    def _clean_up(
        self,
        dir_src: str,
        audio_files: list[AudioFile],
        clutter_files: list[ClutterFile],
    ):
        '''
        Remove empty folders in the given directory.

        Returns true if the given folder was deleted.
        '''
        if self.dry_run:
            logger.dry_run(f'Cleaning up {dir_src} and its subfolders')

        else:
            if not os.path.isdir(dir_src):
                if (
                    dir_src in audio_files
                    or
                    dir_src in clutter_files
                ):
                    remove_file(dir_src, self.dry_run, self.verbose)

            else:
                for filename in os.listdir(dir_src):
                    file = os.path.join(dir_src, filename)
                    self._clean_up(
                        file,
                        audio_files,
                        clutter_files
                    )

                remove_directory(dir_src, self.verbose)
