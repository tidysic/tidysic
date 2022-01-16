# tidysic

Keep your music library tidy.

## Requirements

- `python3.10`
- `poetry`

## Getting Started

Once you cloned the repository and entered the folder, install the required libraries by
running

```sh
poetry install
```

**Note:** from now on, every command given in this `README` will need to be launched
through `poetry`. To do this, either activate `poetry`'s virtual environment using

```sh
poetry shell
```

or prefix the commands with

```sh
poetry run <command>
```

Once ready, you can run the application with:

```sh
tidyisc
```

## Configuration

The music files can be sorted in any possible combination of nested folders that
can be created from their tags. To do so, the desired folder architecture must
be specified either in a `.tidysic` configuration file located in the target folder, or
in another file explicitly given to the program with the `--config` option. The lookup
order is as follow:

1. Config file explicited in the program call
2. `.tidysic` file in the target folder
3. Default configuration

Running

```sh
tidysic --dump-config
```

will print the default configuration in `stdout`, along with an explanation of the
syntax. It is then useful to run

```sh
tidysic --dump-config > ~/Music/.tidysic
```

once, and then modify it as needed.

### Supported tags

- album
- artist
- title
- genre
- tracknumber
- date
