from PyQt5.QtWidgets import QFileDialog


class FolderSelectDialog(QFileDialog):

    def __init__(self, parent, is_input_folder: bool):
        super(FolderSelectDialog, self).__init__(
            parent,
            caption=f"""Select \
                {"input" if is_input_folder else "output"}\
                folder""",
            directory="~"
        )
        self.setFileMode(QFileDialog.DirectoryOnly)
