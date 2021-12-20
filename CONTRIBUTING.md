# How to contribute

If you want to write code for `tidysic`, you should pay attention to these guidelines. Any pull request which does not pass these criterias will be unmergeable.

## Tests

Tests in the `tests` folder should all pass. To check, simply run

```sh
poetry run python -m pytest tests
```

Alternatively, if you already are in poetry's virtual environment, simply run

```sh
python -m pytest tests
```

## Typing

We attempt to use python's type hinting at best we can, and verify with
[`mypy`](https://github.com/python/mypy) if there are no inconsistencies. To
check, simpy run

```sh
poetry run python -m mypy -p tidysic --ignore-missing-imports
```

Alternatively, if you already are in poetry's virtual environment, simply run

```sh
python -m mypy -p tidysic --ignore-missing-imports
```

## Linting

If you use vscode, you might want to use the provided
`vscode/settings.json.default`. It will ensure linting is compliant with our
checks.

If you don't use vscode, please check that `flake8` accepts your code before
submitting your pull request.
