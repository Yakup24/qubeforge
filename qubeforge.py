#!/usr/bin/env python3
"""QubeForge template orchestrator.

QubeForge is a Linux/Qubes-oriented orchestration layer for this repository.
It keeps template intent in JSON profiles, renders a deterministic build plan,
and can hand that plan to the existing Makefile flow when the operator is ready.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import platform
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parent
PROFILES_DIR = ROOT / "profiles"
MANIFESTS_DIR = ROOT / "manifests"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_.+-]*$")
PLAN_SCHEMA = "qubeforge.plan.v1"
MAX_TEMPLATE_NAME_LENGTH = 31
VERSION = "0.1.0"
PROFILE_KEYS = frozenset(
    {
        "name",
        "dist",
        "flavor",
        "options",
        "packages",
        "services",
        "repos",
        "notes",
    }
)


class QubeForgeError(Exception):
    """User-facing error raised by QubeForge."""


@dataclass(frozen=True)
class Profile:
    name: str
    dist: str
    flavor: str
    options: tuple[str, ...]
    packages: tuple[str, ...]
    services: tuple[str, ...]
    repos: tuple[str, ...]
    notes: str

    @property
    def template_name(self) -> str:
        parts = [self.dist]
        if self.flavor:
            parts.append(self.flavor)
        parts.extend(self.options)

        selected: list[str] = []
        for part in parts:
            candidate = "-".join([*selected, part])
            if selected and len(candidate) > MAX_TEMPLATE_NAME_LENGTH:
                break
            selected.append(part)

        return "-".join(selected)[:MAX_TEMPLATE_NAME_LENGTH]

    @property
    def make_env(self) -> dict[str, str]:
        env = {
            "DIST": self.dist,
            "TEMPLATE_FLAVOR": self.flavor,
            "TEMPLATE_OPTIONS": " ".join(self.options),
            "QUBEFORGE_PROFILE": self.name,
            "QUBEFORGE_PACKAGES": " ".join(self.packages),
            "QUBEFORGE_SERVICES": " ".join(self.services),
            "QUBEFORGE_REPOS": " ".join(self.repos),
        }
        return {key: value for key, value in env.items() if value}


def _as_tuple(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if value is None:
        return ()
    if not isinstance(value, list):
        raise QubeForgeError(f"{key} must be a list of strings")

    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise QubeForgeError(f"{key} must contain non-empty strings")
        items.append(item.strip())
    return tuple(items)


def load_profile(name: str) -> Profile:
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        raise QubeForgeError(f"profile not found: {name}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QubeForgeError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise QubeForgeError(f"profile must be a JSON object: {name}")

    unknown_keys = sorted(set(raw) - PROFILE_KEYS)
    if unknown_keys:
        raise QubeForgeError(f"unknown profile keys in {name}: {', '.join(unknown_keys)}")

    profile_name = str(raw.get("name", name)).strip()
    dist = str(raw.get("dist", "")).strip()
    flavor = str(raw.get("flavor", "")).strip()
    notes = str(raw.get("notes", "")).strip()

    if profile_name != name:
        raise QubeForgeError(f"profile name must match file name: {name}")

    for label, value in {"name": profile_name, "dist": dist}.items():
        if not value or not NAME_RE.match(value):
            raise QubeForgeError(f"{label} must match {NAME_RE.pattern}")

    if flavor and not NAME_RE.match(flavor):
        raise QubeForgeError(f"flavor must match {NAME_RE.pattern}")

    options = _as_tuple(raw, "options")
    for option in options:
        if not NAME_RE.match(option):
            raise QubeForgeError(f"option must match {NAME_RE.pattern}: {option}")

    return Profile(
        name=profile_name,
        dist=dist,
        flavor=flavor,
        options=options,
        packages=_as_tuple(raw, "packages"),
        services=_as_tuple(raw, "services"),
        repos=_as_tuple(raw, "repos"),
        notes=notes,
    )


def list_profiles() -> list[str]:
    return sorted(
        path.stem
        for path in PROFILES_DIR.glob("*.json")
        if path.name != "schema.json" and not path.name.startswith(".")
    )


def render_plan(profile: Profile) -> dict[str, Any]:
    timestamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema": PLAN_SCHEMA,
        "created_at": timestamp,
        "profile": profile.name,
        "template_name": profile.template_name,
        "build": {
            "dist": profile.dist,
            "flavor": profile.flavor,
            "options": list(profile.options),
            "legacy_target": "rpms",
        },
        "payload": {
            "packages": list(profile.packages),
            "services": list(profile.services),
            "repos": list(profile.repos),
        },
        "notes": profile.notes,
    }


def write_manifest(profile: Profile, plan: dict[str, Any]) -> pathlib.Path:
    MANIFESTS_DIR.mkdir(exist_ok=True)
    path = MANIFESTS_DIR / f"{profile.template_name}.plan.json"
    path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def print_plan(plan: dict[str, Any]) -> None:
    print(json.dumps(plan, indent=2, sort_keys=True))


def format_env(env: dict[str, str]) -> str:
    return " ".join(f"{key}={shlex.quote(value)}" for key, value in env.items())


def run_build(profile: Profile, manifest_path: pathlib.Path, dry_run: bool) -> int:
    env = os.environ.copy()
    env.update(profile.make_env)
    env["QUBEFORGE_MANIFEST"] = str(manifest_path)
    command = ["make", "rpms"]

    if dry_run:
        qubeforge_env = {**profile.make_env, "QUBEFORGE_MANIFEST": str(manifest_path)}
        print("Dry run: " + format_env(qubeforge_env))
        print("Dry run: " + " ".join(command))
        return 0

    if platform.system() == "Windows":
        raise QubeForgeError("actual builds must run in a Linux/Qubes build environment")

    return subprocess.call(command, cwd=ROOT, env=env)


def command_profiles(_args: argparse.Namespace) -> int:
    for name in list_profiles():
        print(name)
    return 0


def command_plan(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile)
    plan = render_plan(profile)
    if args.write:
        path = write_manifest(profile, plan)
        print(path)
    else:
        print_plan(plan)
    return 0


def command_validate(args: argparse.Namespace) -> int:
    profile_names = [args.profile] if args.profile else list_profiles()
    if not profile_names:
        raise QubeForgeError("no profiles found")

    for profile_name in profile_names:
        profile = load_profile(profile_name)
        print(f"OK {profile.name} -> {profile.template_name}")
    return 0


def command_build(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile)
    plan = render_plan(profile)
    path = write_manifest(profile, plan)
    print(f"Wrote {path}")
    return run_build(profile, manifest_path=path, dry_run=args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qubeforge",
        description="Linux/Qubes profile driven template build orchestration.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    profiles = sub.add_parser("profiles", help="list available profiles")
    profiles.set_defaults(func=command_profiles)

    plan = sub.add_parser("plan", help="render a build plan")
    plan.add_argument("profile", help="profile name from profiles/*.json")
    plan.add_argument("--write", action="store_true", help="write plan into manifests/")
    plan.set_defaults(func=command_plan)

    validate = sub.add_parser("validate", help="validate one profile or all profiles")
    validate.add_argument("profile", nargs="?", help="profile name from profiles/*.json")
    validate.set_defaults(func=command_validate)

    build = sub.add_parser("build", help="write a manifest and run the build")
    build.add_argument("profile", help="profile name from profiles/*.json")
    build.add_argument("--dry-run", action="store_true", help="show the legacy command only")
    build.set_defaults(func=command_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except QubeForgeError as exc:
        print(f"qubeforge: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
