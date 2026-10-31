#!/usr/bin/env python3
"""
Multi-ecosystem SemVer bumper.
Supports:
  - package.json (Node.js)
  - pyproject.toml (Python)
  - Cargo.toml (Rust)
  - VERSION (Plain text)
"""

import sys
import os
import re
import json
import argparse
from typing import Tuple, Optional, Dict, Any

SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

def parse_semver(version_str: str) -> Tuple[int, int, int, Optional[str], Optional[str]]:
    version_str = version_str.strip().lstrip("v")
    match = SEMVER_REGEX.match(version_str)
    if not match:
        raise ValueError(f"Invalid SemVer string: '{version_str}'")
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    prerelease = match.group("prerelease")
    buildmetadata = match.group("buildmetadata")
    return major, minor, patch, prerelease, buildmetadata

def compute_bump(current_version: str, bump_type: str) -> str:
    major, minor, patch, _, _ = parse_semver(current_version)
    bump_type = bump_type.lower()
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unknown bump type '{bump_type}'. Must be major, minor, or patch.")

def find_version_file(search_dir: str = ".") -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Finds the first supported version file in search_dir.
    Returns: (file_type, file_path, current_version)
    """
    # 1. package.json
    pkg_path = os.path.join(search_dir, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "version" in data and isinstance(data["version"], str):
                    return "package.json", pkg_path, data["version"]
        except Exception:
            pass

    # 2. pyproject.toml
    pyproject_path = os.path.join(search_dir, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Matches version = "1.2.3" in [project] or [tool.poetry]
                match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return "pyproject.toml", pyproject_path, match.group(1)
        except Exception:
            pass

    # 3. Cargo.toml
    cargo_path = os.path.join(search_dir, "Cargo.toml")
    if os.path.isfile(cargo_path):
        try:
            with open(cargo_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return "Cargo.toml", cargo_path, match.group(1)
        except Exception:
            pass

    # 4. VERSION file
    version_file_path = os.path.join(search_dir, "VERSION")
    if os.path.isfile(version_file_path):
        try:
            with open(version_file_path, "r", encoding="utf-8") as f:
                ver = f.read().strip()
                if ver:
                    return "VERSION", version_file_path, ver
        except Exception:
            pass

    return None, None, None

def update_version_file(file_type: str, file_path: str, new_version: str) -> None:
    if file_type == "package.json":
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        replaced = False
        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                if not replaced and re.search(r'"version"\s*:\s*"[^"]*"', line):
                    line = re.sub(r'"version"\s*:\s*"[^"]*"', f'"version": "{new_version}"', line)
                    replaced = True
                f.write(line)

    elif file_type in ("pyproject.toml", "Cargo.toml"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = re.sub(
            r'(?m)^version\s*=\s*["\'][^"\']+["\']',
            f'version = "{new_version}"',
            content,
            count=1
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    elif file_type == "VERSION":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_version + "\n")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def main():
    parser = argparse.ArgumentParser(description="Universal SemVer version bumper")
    parser.add_argument("--dir", default=".", help="Directory to search for version file")
    parser.add_argument("--check", action="store_true", help="Print current detected version and exit")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump type (major, minor, patch)")
    parser.add_argument("--set", dest="set_version", help="Explicit version string to set")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes to disk")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    file_type, file_path, current_version = find_version_file(args.dir)

    if not file_type or not current_version:
        res = {"status": "error", "message": f"No supported version file found in {args.dir}"}
        if args.json:
            print(json.dumps(res))
        else:
            print(f"Error: {res['message']}", file=sys.stderr)
        sys.exit(1)

    if args.check or (not args.bump and not args.set_version):
        res = {
            "status": "ok",
            "file_type": file_type,
            "file_path": os.path.abspath(file_path),
            "current_version": current_version
        }
        if args.json:
            print(json.dumps(res))
        else:
            print(f"File: {file_path} ({file_type})")
            print(f"Current version: {current_version}")
        sys.exit(0)

    if args.set_version:
        new_version = args.set_version.strip().lstrip("v")
        # Validate semver
        parse_semver(new_version)
    else:
        new_version = compute_bump(current_version, args.bump)

    if not args.dry_run:
        update_version_file(file_type, file_path, new_version)

    res = {
        "status": "ok",
        "file_type": file_type,
        "file_path": os.path.abspath(file_path),
        "previous_version": current_version,
        "new_version": new_version,
        "dry_run": args.dry_run
    }

    if args.json:
        print(json.dumps(res))
    else:
        action = "[DRY-RUN] Would update" if args.dry_run else "Updated"
        print(f"{action} {file_path}: {current_version} -> {new_version}")

if __name__ == "__main__":
    main()
