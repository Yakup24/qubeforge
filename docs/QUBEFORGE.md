# QubeForge Template Builder

QubeForge turns this repository into a Linux/Qubes profile-driven template build
system.  The old scripts still do the privileged image and RPM work, while
QubeForge provides a safer front door:

- JSON profiles in `profiles/`
- deterministic build manifests in `manifests/`
- validation before privileged work
- dry-run support before privileged build steps
- a single CLI for listing, planning, and building

## Commands

List profiles:

```sh
python3 qubeforge.py profiles
```

Show the CLI version:

```sh
python3 qubeforge.py --version
```

Validate profiles:

```sh
python3 qubeforge.py validate
```

Render a plan:

```sh
python3 qubeforge.py plan debian-vault
```

Write a manifest without building:

```sh
python3 qubeforge.py plan debian-vault --write
```

Show the legacy build command that would run:

```sh
python3 qubeforge.py build debian-vault --dry-run
```

Run the build:

```sh
python3 qubeforge.py build debian-vault
```

## Profile Shape

Each profile is a JSON document:

```json
{
  "name": "debian-vault",
  "dist": "debian-12",
  "flavor": "vault",
  "options": ["minimal", "audit", "hardened"],
  "packages": ["qubes-core-agent", "auditd"],
  "services": ["auditd"],
  "repos": ["qubes-current"],
  "notes": "Security-focused Debian vault template for Qubes compartments."
}
```

QubeForge writes the plan first, then bridges into the existing `make rpms`
target by exporting:

- `DIST`
- `TEMPLATE_FLAVOR`
- `TEMPLATE_OPTIONS`
- `QUBEFORGE_PROFILE`
- `QUBEFORGE_PACKAGES`
- `QUBEFORGE_SERVICES`
- `QUBEFORGE_REPOS`
- `QUBEFORGE_MANIFEST`

## Build Environment

Real builds must run in a Linux/Qubes build environment.  On other development
machines, use `--dry-run` to inspect the generated manifest and the environment
that would be passed to `make rpms`.
