# tidysic

Keep your music library tidy.

## Requirements

- `python3.9`
- `poetry`

## Getting Started

Once you cloned the repository and entered the folder, you can run the
application with:

1. `poetry run tidysic`
2. Alternatively, once inside the virtual environment created via `poetry shell`,
   just run `tidysic`


## Pattern

The music files can be sorted in any possible combination of nested folders that
can be created from their tags. To do so, the desired folder architecture must
be specified through the `pattern` argument. The `pattern` must a be string of
"slash-separated" tag names, e.g.:

```
genre/artist/album
```

Will create one folder per existing `genre` in the library. Each genre folder
will contain one folder per `artist` tagged with this `genre`. And finally, each
artist folder will contain one folder per `album`.

### Supported tags

- album
- artist
- title
- genre
- tracknumber
- date
