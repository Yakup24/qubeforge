# Build Environment

QubeForge can render and validate profiles on any host with Python 3.10 or
newer.  Real template builds must run in a Linux/Qubes-oriented build
environment because the inherited pipeline uses `make`, `sudo`, RPM tooling, and
image manipulation scripts.

## Preflight

Run:

```sh
python3 qubeforge.py doctor --profile debian-vault
```

The preflight checks:

- repository build primitives are present
- the selected profile resolves to a valid template name
- the host is not Windows for real build execution
- required build tools are available on `PATH`

For CI jobs that only validate profile shape and repository layout, tool checks
can be skipped:

```sh
python3 qubeforge.py doctor --profile debian-vault --skip-tools
```

## Required Tooling

QubeForge checks for:

- `bash`
- `make`
- `sudo`
- `rpm`
- `rpmbuild`

The broader Qubes builder environment may need additional packages depending on
the template distribution and plugin set.

## References

- Qubes builder documentation: https://dev.qubes-os.org/en/latest/developer/building/qubes-builder.html
- Qubes templates documentation: https://doc.qubes-os.org/en/latest/user/templates/templates.html
