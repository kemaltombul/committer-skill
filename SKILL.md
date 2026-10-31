---
name: committer
description: >-
  Use this skill whenever the user asks to commit changes, create a git commit, bump project versions,
  write detailed Conventional Commit messages, organize atomic commits, or maintain CHANGELOG.md.
---

# Committer Skill Runbook

This skill guides the agent through an intelligent, safe, and structured git workflow: analyzing repository changes, splitting unrelated modifications into atomic commits, calculating Semantic Version bumps across project ecosystems, formatting detailed Conventional Commit messages, maintaining `CHANGELOG.md`, and previewing all staged diffs for user confirmation prior to committing.

---

## Workflow Steps

### Step 1: Inspect Working Tree & Diffs
Run the following commands to assess the current repository state:
```bash
git status --short
git diff --stat
```
1. Check which files are modified, untracked, or already staged.
2. If there are untracked files that should be ignored, ensure they are in `.gitignore`.
3. Read the actual line diffs using `git diff` (and `git diff --cached` if files are pre-staged).

---

### Step 2: Atomic Commit Analysis & Staging
1. **Analyze Change Scope**:
   - Are there multiple unrelated features, bug fixes, or refactors mixed in the working tree?
   - If yes, **do not commit everything together**. Group files logically into separate atomic commits (e.g., Commit 1: `fix(auth): ...`, Commit 2: `feat(dashboard): ...`).
2. **Stage Targeted Files**:
   - Stage only the files belonging to the current atomic commit unit:
     ```bash
     git add <file1> <file2>
     ```
   - Avoid `git add .` or `git add -A` when multiple concerns exist.

---

### Step 3: Change Classification & SemVer Calculation
Determine the primary type of change according to [Conventional Commits](./references/conventional_commits.md):
- **Major (`BREAKING CHANGE`)**: Incompatible API changes, breaking signature alterations, or removed deprecations.
- **Minor (`feat`)**: New user-facing or system functionality.
- **Patch (`fix`, `perf`, `refactor`)**: Bug fixes or performance improvements.
- **None / Skip**: Documentation (`docs`), formatting (`style`), tests (`test`), or minor chores (`chore`).

Review [SemVer Rules & Mapping](./references/semver_rules.md) for detailed guidelines.

---

### Step 4: Execute Version Bump (If Applicable)
Use the automated version bumper helper script:

1. **Check Current Version**:
   ```bash
   python3 ~/.gemini/config/skills/committer/scripts/bump_version.py --check
   # (Or: python3 .agents/skills/committer/scripts/bump_version.py --check)
   ```
2. **Dry-Run Proposed Bump**:
   ```bash
   python3 ~/.gemini/config/skills/committer/scripts/bump_version.py --bump [major|minor|patch] --dry-run
   ```
3. **Apply Version Bump**:
   If a version increment is warranted and agreed upon:
   ```bash
   python3 ~/.gemini/config/skills/committer/scripts/bump_version.py --bump [major|minor|patch]
   ```
   *Stage the updated version file:*
   ```bash
   git add package.json # or pyproject.toml / Cargo.toml / VERSION
   ```

---

### Step 5: Draft Detailed Conventional Commit Message
Construct the commit message following this precise structure:
```text
<type>(<scope>): <imperative summary under 72 characters>

<Why paragraph: Problem statement, motivation, and architectural rationale>

<Bulleted technical breakdown of modified components>
* <Component A>: <Specific modification>
* <Component B>: <Specific modification>

[BREAKING CHANGE: <Explanation of breaking change and migration path>]
[Closes #<issue_number>]
```

#### Formatting Rules:
- **Header**: Imperative mood ("add", "fix", "refactor", not "added" or "fixing"). No period at the end.
- **Body**: Answer **why** the change was made, not just repeating line diffs.
- **Bullets**: Detail specific architectural decisions and notable functional changes.

---

### Step 6: Maintain `CHANGELOG.md` (If Present)
If `CHANGELOG.md` exists in the repository root:
1. Locate the top release section.
2. Prepend a new section for the bumped version:
   ```markdown
   ## [<new_version>] - <YYYY-MM-DD>

   ### Added / Fixed / Changed
   - <Summary of modification>
   ```
3. Stage the changelog:
   ```bash
   git add CHANGELOG.md
   ```

---

### Step 7: Confirmation & Verification Gate
Before running `git commit`, present a concise preview to the user:
1. **Staged Files Summary**: List of all files in the current commit.
2. **Version Bump**: Previous version -> New version (or "No version bump").
3. **Commit Message Preview**: The exact subject, body, and breakdown.
4. Ask the user for confirmation to execute the commit.

---

### Step 8: Execute Git Commit
Once approved:
```bash
git commit -m "<header>" -m "<body>" -m "<breakdown>"
```
*(Or use a temporary message file / heredoc for clean multi-line formatting without shell escape issues).*

If a new version was bumped and a git tag is requested:
```bash
git tag -a "v<new_version>" -m "Release v<new_version>"
```
Verify the commit with:
```bash
git log -1 --stat
```
