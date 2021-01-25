# tidysic

Keep your music library tidy

## Dev

The current `requirements.txt` assume that you have PyQt5 already installed through your OS's repository (for instance, using `apt` for Debian-based GNU/Linux distribution, or `brew` for MacOS). The purpose behind this choice is a better integration of the app into your system's theme during the development process. This can and probably will be changed later on. If you don't want the hassle, installing through `pip` once the virtualenv is setup should work.

### Running the app

The lightweight scripts `cli_tool` and `ui_tool` allow to run either version of the app from the root of the project.

### Test

A test file name must start with *test*.

* python -m unittest discover
