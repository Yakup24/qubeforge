# Contributing

QubeForge keeps the low-level Qubes template scripts intact and adds a small,
testable orchestration layer on top.

## Local Checks

Run the Python tests:

```sh
python3 -m unittest discover -s tests -p "test_*.py"
```

Validate profiles:

```sh
python3 qubeforge.py validate
```

Preview a build without privileged image work:

```sh
python3 qubeforge.py build debian-vault --dry-run
```

## Profile Rules

- Profile file names must match the `name` field.
- `name`, `dist`, `flavor`, and `options` use lowercase slug-style values.
- `packages`, `services`, and `repos` are explicit lists of strings.
- Generated manifests are build artifacts and should not be committed.

## Pull Requests

Keep changes focused.  If a change affects the legacy Bash build path, include a
dry-run command or a clear manual verification note.
