# README Synchronization & Pre-Commit Integration

This reference describes the architectural design and operational protocol for integrating the `readme-r` automatic documentation synchronization skill into the `committer` git workflow.

---

## 1. Problem Statement & Motivation

During fast-paced software development and agentic code modification:
- New API endpoints, CLI flags, configuration variables, and architectural layers are added.
- `README.md` files frequently become outdated because documentation updates are deferred or overlooked.
- Release tags and version bumps are pushed with stale or incomplete documentation.

The `git-release-toolkit` prevents documentation drift by embedding a **README Synchronization Audit Gate (Step 2)** directly into the pre-commit staging pipeline of `committer`.

---

## 2. Helper Resolution Protocol

When `committer` executes change detection, it attempts to resolve `detect_changes.py` through the following precedence:

1. **Sibling Skill in Plugin Bundle**:
   `../readme-r/scripts/detect_changes.py`
2. **Plugin Relative Root**:
   `skills/readme-r/scripts/detect_changes.py`
3. **Global User Configuration**:
   `~/.gemini/config/skills/readme-r/scripts/detect_changes.py`
4. **Project-Local Agent Customization**:
   `.agents/skills/readme-r/scripts/detect_changes.py`

---

## 3. Decision Matrix & Staging Strategies

| Change Scenario | Action Taken | Staging Strategy |
| :--- | :--- | :--- |
| **New Feature / Route / Component** | Run `detect_changes.py`; perform contextual merge on `README.md` to document new capability | Stage `README.md` alongside the feature files in the atomic `feat:` commit. |
| **Dependency Manifest Change** (`package.json`, `Cargo.toml`, etc.) | Detect manifest modification; update Prerequisites or Installation sections | Stage `README.md` with manifest update in the `build:` or `chore:` commit. |
| **Environment Variable Added** (`.env.example`) | Extract new variable keys; update Configuration table | Stage `README.md` and `.env.example` together in the atomic commit. |
| **Multi-concern or Cross-Cutting Refactor** | Run contextual merge across root and hierarchical READMEs | Stage documentation updates as an independent `docs(readme): synchronize documentation` atomic commit. |
| **Internal Chore / Style / Pure Docs Edit** | Verify that `README.md` is accurate and current | No additional README edits required; proceed directly to atomic commit staging. |

---

## 4. Contextual Merge Principles

When updating existing documentation:
- **Preserve**: Never discard custom branding, shields/badges, voice/tone, architectural callouts, or human-authored disclaimers.
- **Surgically Insert / Update**:
  - Features bullet list
  - Architecture diagram (`mermaid`)
  - Configuration tables
  - CLI usage tables
  - Submodule directory maps
- **Generate if Missing**: If a project or new submodule has no `README.md`, scaffold a complete front-page using the standard blueprint in `../readme-r/resources/standard_template.md`.
