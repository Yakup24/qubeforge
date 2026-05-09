# QubeForge Template Builder

[![CI](https://github.com/Yakup24/qubeforge/actions/workflows/ci.yml/badge.svg)](https://github.com/Yakup24/qubeforge/actions/workflows/ci.yml)

QubeForge is a profile-driven orchestration layer for Qubes OS Linux template
builds.  It keeps the existing low-level image and RPM scripts in place, then
adds a clean command-line interface for profile validation, deterministic plan
generation, and controlled handoff to `make rpms`.

This project is intended for Linux/Qubes build environments.  Running a real
template build requires the same privileges and tooling as the original template
builder; `--dry-run` is available for safe review on any development machine.

## Features

- JSON profiles for repeatable template definitions
- deterministic build plans written to `manifests/`
- profile validation before privileged build work
- host preflight checks with `doctor`
- `QUBEFORGE_*` environment handoff for custom build plugins
- Makefile targets for common workflows
- Python unit tests and GitHub Actions CI
- example Debian and Fedora template profiles

## Quick Start

List profiles:

```sh
python3 qubeforge.py profiles
```

Show the CLI version:

```sh
python3 qubeforge.py --version
```

Validate all profiles:

```sh
python3 qubeforge.py validate
```

Check host build readiness:

```sh
python3 qubeforge.py doctor --profile debian-vault
```

Render a plan:

```sh
python3 qubeforge.py plan debian-vault
```

Write a plan to a specific file:

```sh
python3 qubeforge.py plan debian-vault --output /tmp/debian-vault.plan.json
```

Write a manifest without building:

```sh
python3 qubeforge.py plan debian-vault --write
```

Preview the legacy build handoff:

```sh
python3 qubeforge.py build debian-vault --dry-run
```

Run a template build in a Linux/Qubes build environment:

```sh
python3 qubeforge.py build debian-vault
```

## Install

The CLI has no third-party Python dependencies.

```sh
python3 -m pip install -e .
qubeforge validate
```

## Make Targets

```sh
make qubeforge-profiles
make qubeforge-validate
make qubeforge-doctor
make qubeforge-plan PROFILE=debian-vault
make qubeforge-build PROFILE=debian-vault
make test
```

## Profile Format

Profiles live in `profiles/*.json`.  The file name must match the `name` field.

```json
{
  "name": "debian-vault",
  "dist": "debian-12",
  "flavor": "vault",
  "options": ["minimal", "audit", "hardened"],
  "packages": ["qubes-core-agent", "auditd"],
  "services": ["auditd"],
  "repos": ["qubes-current", "debian-security"],
  "notes": "Security-focused Debian vault template for Qubes compartments."
}
```

The generated template name is kept within Qubes' 31-character VM name limit.

## Repository Layout

- `qubeforge.py` is the orchestration CLI.
- `profiles/` contains template profiles and `schema.json`.
- `docs/QUBEFORGE.md` contains deeper usage notes.
- `docs/BUILD_ENVIRONMENT.md` documents host preflight expectations.
- `examples/` contains checked-in sample outputs.
- `manifests/` contains generated build plans and is ignored by Git.
- `prepare_image`, `qubeize_image`, and `build_template_rpm` remain the
  low-level build primitives.

## Upstream Relationship

QubeForge is an orchestration layer built on top of the inherited Qubes template
builder scripts.  See `NOTICE.md` before publishing or redistributing the
repository.

## Development

Run the local checks:

```sh
python3 -m unittest discover -s tests -p "test_*.py"
python3 qubeforge.py validate
python3 qubeforge.py build debian-vault --dry-run
```

## Publishing Notes

The inherited Qubes source licensing model is documented in `LICENSE`.
