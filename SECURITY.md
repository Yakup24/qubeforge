# Security Policy

QubeForge builds operating system templates.  Treat profile changes and build
scripts as privileged infrastructure changes.

## Reporting Issues

Do not publish sensitive build logs, private repository URLs, signing keys, or
template artifacts in a public issue.  Open a private report through your Git
hosting provider or contact the repository maintainers directly.

## Build Safety

- Run real builds only inside a Linux/Qubes build environment.
- Review generated manifests before invoking privileged build steps.
- Keep signing keys outside the repository.
- Do not commit generated images, RPMs, or manifests.
