# Conventional Commits Specification & Guide

This reference outlines the Conventional Commits specification (v1.0.0) format, types, scopes, and best practices for creating detailed, human- and machine-readable git commit messages.

---

## 1. Structure of a Conventional Commit

Every commit message produced by the `committer` skill follows this structure:

```text
<type>[optional scope]: <imperative description>

[optional body: context & architectural reasoning]

[optional technical breakdown: bulleted list of changes]

[optional footer(s): breaking changes, closed issues]
```

### Example Full Commit Message

```text
feat(auth): implement refresh token rotation and revocation

Previously, JWT access tokens were refreshed indefinitely without server-side
state tracking, exposing accounts to persistent replay attacks if a refresh token
leaked. This change introduces Redis-backed refresh token rotation with family
revocation upon duplicate presentation.

* Add `RefreshTokenStore` interface and Redis implementation in `storage/`
* Extend `/api/auth/refresh` route with token rotation middleware
* Add migration for revoked token family tracking table
* Implement unit tests in `tests/test_auth_rotation.py`

BREAKING CHANGE: The refresh endpoint now requires the `client_id` header in requests.
Closes #142
```

---

## 2. Commit Types

| Type | Intent | SemVer Default | Description |
| :--- | :--- | :--- | :--- |
| **`feat`** | New feature | **Minor** | Adds new functionality for the user or system |
| **`fix`** | Bug fix | **Patch** | Solves a bug or unexpected behavior in code |
| **`perf`** | Performance | **Patch** | Changes code to improve execution speed or memory usage |
| **`refactor`** | Refactoring | **Patch** (or skip) | Code restructuring without fixing a bug or adding a feature |
| **`docs`** | Documentation | Skip (or patch) | Changes to README, docs, docstrings, or markdown guides |
| **`style`** | Code style | Skip | Formatting, missing semi-colons, whitespace (no logic change) |
| **`test`** | Testing | Skip | Adding missing tests or correcting existing tests |
| **`build`** | Build system | Patch / Skip | Changes that affect build tool, dependencies (`package.json`, build scripts) |
| **`ci`** | CI / CD | Skip | Changes to CI configuration files and scripts (`.github/workflows`) |
| **`chore`** | Maintenance | Skip / Patch | Miscellaneous maintenance tasks, cleaning temp code, updates |
| **`revert`** | Reverts | Depends | Reverts a previous commit |

---

## 3. Scopes

The scope describes the codebase section or module affected by the commit:
- Common examples: `api`, `auth`, `ui`, `db`, `cli`, `config`, `deps`, `worker`, `core`.
- Keep scopes lowercase, concise, and consistent across commits.

---

## 4. Subject Line Rules

1. **Imperative Mood**: Use imperative verbs ("add", "fix", "update", "remove", not "added" or "adds").
2. **Length**: Keep under 72 characters (ideally ~50 characters).
3. **Punctuation**: No trailing period (`.`) at the end of the subject line.
4. **Casing**: Lowercase first letter after the colon (e.g., `feat(ui): add dark mode switch`).

---

## 5. Body & Breakdown

- **The "Why" Paragraph**: Always explain the problem being solved or the motivation behind the change, rather than merely re-stating what the code does.
- **Bulleted Breakdown**: When changes span multiple files or components, itemize specific modifications to make reviews effortless:
  - `* Implement ...`
  - `* Fix ...`
  - `* Update ...`

---

## 6. Footers & Breaking Changes

- **Breaking Changes**: Must start with `BREAKING CHANGE:` followed by a space or two newlines, describing what broke and how to migrate. Alternatively, use an exclamation mark after type/scope (e.g., `feat(api)!: remove deprecated v1 endpoint`).
- **Issue References**: E.g., `Closes #123`, `Fixes #45`, `Refs #89`.
