# Semantic Versioning 2.0.0 & Changelog Maintenance

This reference guide details SemVer 2.0.0 calculation rules, supported project configuration files, and `CHANGELOG.md` format standards used by the `committer` skill.

---

## 1. SemVer 2.0.0 Mapping

A Semantic Version takes the format `MAJOR.MINOR.PATCH`:
- **MAJOR** (`X.0.0`): Incompatible API or structural breaking changes.
- **MINOR** (`x.Y.0`): Backwards-compatible new features.
- **PATCH** (`x.y.Z`): Backwards-compatible bug fixes and internal refactors.

### Decision Matrix

| Commit Content / Type | Bump Level | Example Transition |
| :--- | :--- | :--- |
| `BREAKING CHANGE:` footer or `type!:` syntax | **MAJOR** | `1.4.2` -> `2.0.0` |
| `feat:` (New feature) | **MINOR** | `1.4.2` -> `1.5.0` |
| `fix:`, `perf:` (Bug fixes, performance improvements) | **PATCH** | `1.4.2` -> `1.4.3` |
| `refactor:`, `build:` with operational impact | **PATCH** | `1.4.2` -> `1.4.3` |
| `docs:`, `style:`, `test:`, `ci:`, `chore:` without release impact | **Skip** (or optional patch) | Unchanged / user choice |

---

## 2. Multi-Ecosystem File Support

The `committer` skill automatically discovers and updates version files in order of precedence:

1. **Node.js**: `package.json` (`"version": "x.y.z"`). If `package-lock.json` exists, running `npm --package-lock-only` or updating version keeps it in sync.
2. **Python**: `pyproject.toml` (`version = "x.y.z"` under `[project]` or `[tool.poetry]`).
3. **Rust**: `Cargo.toml` (`version = "x.y.z"` under `[package]`).
4. **Generic**: `VERSION` (plain text containing solely the semver string).

---

## 3. `CHANGELOG.md` Maintenance (Keep a Changelog Format)

If a `CHANGELOG.md` exists in the repository root, the skill automatically updates it using the [Keep a Changelog](https://keepachangelog.com/) standard:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-10-31

### Added
- Refresh token rotation middleware and revocation tracking.

### Changed
- Refactored token validation pipeline to support Redis caching.

### Fixed
- Resolved race condition during concurrent refresh calls (#102).

### Breaking Changes
- Client application must provide `client_id` header in token refresh payload.
```

### Categorization Mapping

- `feat` -> `### Added`
- `fix` -> `### Fixed`
- `refactor`, `perf` -> `### Changed`
- `deprecate` -> `### Deprecated`
- Removal of features -> `### Removed`
- `BREAKING CHANGE` -> `### Breaking Changes`
- Security patches -> `### Security`
