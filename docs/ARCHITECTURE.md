# Architecture

QubeForge is intentionally thin.  It does not replace the inherited Qubes
template build scripts; it adds a typed, testable orchestration layer in front
of them.

## Flow

```text
profiles/*.json
      |
      v
qubeforge.py validate
      |
      v
qubeforge.py plan
      |
      v
manifests/*.plan.json
      |
      v
qubeforge.py build
      |
      v
make rpms -> prepare_image -> qubeize_image -> build_template_rpm
```

## Boundaries

QubeForge owns:

- profile loading and validation
- deterministic plan rendering
- host preflight checks
- environment handoff to the legacy build path

The legacy scripts own:

- root image preparation
- Qubes-specific image mutation
- RPM packaging
- repository installation helpers

## Design Notes

- Generated manifests are artifacts and are ignored by Git.
- Template names are capped at 31 characters to match Qubes VM name limits.
- Omitted name parts are recorded in the plan so name shortening is visible.
- Real builds are blocked on Windows before privileged build work starts.
