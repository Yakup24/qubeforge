# QubeForge Template Builder

[![CI](https://github.com/Yakup24/qubeforge/actions/workflows/ci.yml/badge.svg)](https://github.com/Yakup24/qubeforge/actions/workflows/ci.yml)

QubeForge adds a small profile layer to an inherited Qubes Linux template
builder. Profiles describe the distribution, flavor, packages, services, and
repository inputs for a template. The CLI validates those profiles, writes a
build plan, and then hands off to the existing `make rpms` path.

The legacy image and RPM scripts still do the privileged work. QubeForge is the
operator-facing layer in front of them: it makes intent explicit before a build
touches root images or packaging steps.

Real builds are meant to run in a Linux/Qubes build environment. On other
machines, use `--dry-run`, `validate`, and `doctor --skip-tools` to review
profiles and generated plans without starting privileged image work.

## Status

This is an early orchestration layer, not a replacement for the Qubes builder.
The current focus is profile validation, reproducible plan output, and safe
handoff into the existing scripts. A full Linux/Qubes build verification is
tracked in `ROADMAP.md`.

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
