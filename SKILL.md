---
name: committer
description: >-
  Use this skill whenever the user asks to commit changes, create a git commit, bump project versions,
  synchronize README documentation via readme-r, write detailed Conventional Commit messages, organize atomic commits,
  maintain CHANGELOG.md, or safely push commits and tags to remote repositories with authentication and environment validation.
---

# Committer Skill Runbook

This skill guides the agent through an intelligent, safe, and structured git workflow: analyzing repository changes, auditing environment variables and secrets, verifying README documentation synchronization via `readme-r`, splitting unrelated modifications into atomic commits, calculating Semantic Version bumps across project ecosystems, formatting detailed Conventional Commit messages, maintaining `CHANGELOG.md`, previewing all staged diffs for user confirmation prior to committing, and validating remote destinations & authentication to push commits and tags.

---

## Workflow Steps

### Step 1: Inspect Working Tree, Secrets & Diffs
Run the following commands to assess the current repository state:
```bash
git status --short
git diff --stat
```
1. Check which files are modified, untracked, or already staged.
2. **Environment & Secret Hygiene Audit**:
   - Check that `.env`, `.env.*` (except `.env.example`), private keys (`*.pem`, `*.key`), and `credentials.json` are present in `.gitignore`.
   - Ensure no secret files are tracked or staged (`git ls-files | grep -E '\.env$|\.key$|\.pem$|credentials\.json$'`).
   - If `.env` exists in the project root, ensure a sanitized `.env.example` template is maintained.
3. Read the actual line diffs using `git diff` (and `git diff --cached` if files are pre-staged).

---

### Step 2: README Synchronization Audit (via `readme-r`)
Before staging commits or calculating version bumps, verify that repository documentation has not fallen behind code modifications:

1. **Locate `readme-r`**:
   Resolve the change detector helper using the first available path:
   - Sibling skill in bundle: `../readme-r/scripts/detect_changes.py`
   - Plugin root: `skills/readme-r/scripts/detect_changes.py`
   - Global skill: `~/.gemini/config/skills/readme-r/scripts/detect_changes.py`
   - Project-local skill: `.agents/skills/readme-r/scripts/detect_changes.py`

2. **Execute Change Detection**:
   ```bash
   python3 <resolved_path>/detect_changes.py --json
   ```

3. **Evaluate Documentation State**:
   - **If code, manifests, or `.env` changed but `README.md` is unupdated or missing**:
     Execute the `readme-r` workflow:
     - *Existing README*: Perform contextual merge preserving branding, voice, badges, and untouched sections while updating features, configuration tables, CLI options, and file trees.
     - *Missing README*: Generate a comprehensive front-page using the standard template in `../readme-r/resources/standard_template.md`.
   - **If only docs, styles, or tests changed**: Confirm `README.md` is accurate and proceed.

4. **Staging Strategy for README Changes**:
   - If documenting a single new feature or fix, stage `README.md` directly into that atomic commit.
   - If documentation changes are broad, refactoring, or cross-cutting, stage them as a dedicated `docs(readme): synchronize documentation` atomic commit.

---

### Step 3: Atomic Commit Analysis & Staging
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

### Step 4: Change Classification & SemVer Calculation
Determine the primary type of change according to [Conventional Commits](./references/conventional_commits.md):
- **Major (`BREAKING CHANGE`)**: Incompatible API changes, breaking signature alterations, or removed deprecations.
- **Minor (`feat`)**: New user-facing or system functionality.
- **Patch (`fix`, `perf`, `refactor`)**: Bug fixes or performance improvements.
- **None / Skip**: Documentation (`docs`), formatting (`style`), tests (`test`), or minor chores (`chore`).

Review [SemVer Rules & Mapping](./references/semver_rules.md) for detailed guidelines.

---

### Step 5: Execute Version Bump (If Applicable)
Use the automated version bumper helper script:

1. **Check Current Version**:
   ```bash
   python3 scripts/bump_version.py --check
   # (Or: python3 ~/.gemini/config/plugins/git-release-toolkit/skills/committer/scripts/bump_version.py --check)
   ```
2. **Dry-Run Proposed Bump**:
   ```bash
   python3 scripts/bump_version.py --bump [major|minor|patch] --dry-run
   ```
3. **Apply Version Bump**:
   If a version increment is warranted and agreed upon:
   ```bash
   python3 scripts/bump_version.py --bump [major|minor|patch]
   ```
   *Stage the updated version file:*
   ```bash
   git add package.json # or pyproject.toml / Cargo.toml / VERSION
   ```

---

### Step 6: Draft Detailed Conventional Commit Message
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

### Step 7: Maintain `CHANGELOG.md` (If Present)
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

### Step 8: Confirmation & Verification Gate
Before running `git commit`, present a concise preview to the user:
1. **Staged Files Summary**: List of all files in the current commit.
2. **Version Bump**: Previous version -> New version (or "No version bump").
3. **Commit Message Preview**: The exact subject, body, and breakdown.
4. Ask the user for confirmation to execute the commit.

---

### Step 9: Execute Git Commit
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

---

### Step 10: Push to Remote, Destination Resolution & Auth Control
After a successful commit, ask the user if they would like to push to a remote repository.
Consult [Remote Auth & Env Reference](./references/remote_auth_env.md) for detailed protocols.

1. **Resolve Remote Destination**:
   - Inspect existing remotes:
     ```bash
     git remote -v
     ```
   - **If remotes exist**:
     Identify current branch (`git branch --show-current`).
     Confirm the target remote (e.g., `origin`) and branch with the user.
   - **If no remote is configured**:
     Ask the user for the remote repository URL (`git@github.com:<owner>/<repo>.git` or `https://github.com/<owner>/<repo>.git`).
     Add the remote and link tracking:
     ```bash
     git remote add origin <remote_url>
     ```

2. **Verify & Control Authentication**:
   - **SSH Remote (`git@...`)**:
     Test connectivity:
     ```bash
     ssh -T -o BatchMode=yes -o ConnectTimeout=5 git@<host>
     ```
     If auth fails (`Permission denied`), guide the user to add their key via `ssh-add` or generate an SSH key.
   - **HTTPS Remote (`https://...`)**:
     If using GitHub, verify with `gh auth status`.
     If auth fails, provide remediation (`gh auth login -h github.com`).
     Check for `GITHUB_TOKEN` or `GH_TOKEN` environment variables if automated.
   - **Pre-Flight Dry Run**:
     ```bash
     git push --dry-run <remote> <branch>
     ```

3. **Execute Push with Tags**:
   Once destination and authentication are validated:
   ```bash
   git push -u --follow-tags <remote> <branch>
   ```
   *(If upstream tracking is already set, `git push --follow-tags <remote> <branch>` is sufficient).*
