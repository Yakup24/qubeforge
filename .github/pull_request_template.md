## Summary

Describe the change and why it is needed.

## Verification

- [ ] `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] `python3 qubeforge.py validate`
- [ ] `python3 qubeforge.py build debian-vault --dry-run`

## Build Impact

Note whether this changes profile validation, manifest output, or the legacy
`make rpms` path.
