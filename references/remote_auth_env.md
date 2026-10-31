# Remote Authentication, Environment & Push Management

This reference guides the agent and developers through managing remote git repositories, validating authentication protocols, controlling environment variables and secrets, and safely pushing commits and tags.

---

## 1. Remote Destination Resolution

### Check Existing Remotes
```bash
git remote -v
```

- **If remotes exist** (e.g., `origin`, `upstream`):
  Determine the current branch:
  ```bash
  git branch --show-current
  ```
  Confirm the target remote and branch with the user before pushing.

- **If no remote is configured**:
  Prompt the user for the remote repository URL:
  - **SSH Format**: `git@github.com:<owner>/<repo>.git`
  - **HTTPS Format**: `https://github.com/<owner>/<repo>.git`

  Add the remote and configure upstream tracking:
  ```bash
  git remote add origin <remote_url>
  git push -u origin <current_branch>
  ```

---

## 2. Authentication Verification & Control

Always verify authentication before attempting a push to avoid abrupt failures or hanging processes.

### Protocol A: SSH (`git@...` or `ssh://...`)
1. **Connectivity Check**:
   ```bash
   ssh -T -o BatchMode=yes -o ConnectTimeout=5 git@github.com
   ```
   *(Replace `github.com` with `gitlab.com` or custom host if applicable).*
2. **Success Signature**:
   `Hi <username>! You've successfully authenticated...` (Exit code 1 on GitHub is normal for `ssh -T`).
3. **If Auth Fails (`Permission denied (publickey)`)**:
   - Check if SSH agent is running:
     ```bash
     eval "$(ssh-agent -s)"
     ssh-add -l
     ```
   - Add identity key:
     ```bash
     ssh-add ~/.ssh/id_ed25519 # or id_rsa
     ```
   - If no key exists, guide key generation:
     ```bash
     ssh-keygen -t ed25519 -C "your_email@example.com"
     ```

### Protocol B: HTTPS (`https://...`)
1. **GitHub CLI Status Check**:
   If `gh` is installed:
   ```bash
   gh auth status
   ```
2. **If Token / Auth is Invalid**:
   Remediate with:
   ```bash
   gh auth login -h github.com
   ```
3. **Environment Tokens**:
   Git operations can utilize `GH_TOKEN` or `GITHUB_TOKEN`:
   ```bash
   echo $GH_TOKEN
   echo $GITHUB_TOKEN
   ```
4. **Git Credential Helper**:
   Check configured credential helper:
   ```bash
   git config --get credential.helper
   ```

### Pre-Flight Dry Run
Run a non-destructive push test to validate permissions and branch status:
```bash
git push --dry-run <remote> <branch>
```

---

## 3. Environment Variables & Secret Hygiene

### Secret Safety Rules
1. **Never Commit Secrets**:
   - `.env`, `.env.local`, `.env.*.local`, `credentials.json`, `*.pem`, `*.key` must be listed in `.gitignore`.
2. **Verify Ignore Rules**:
   Ensure `.gitignore` contains:
   ```gitignore
   .env
   .env.*
   !.env.example
   *.pem
   *.key
   credentials.json
   ```
3. **Audit Before Push**:
   Verify no sensitive files are tracked:
   ```bash
   git ls-files | grep -E '\.env$|\.key$|\.pem$|credentials\.json$'
   ```
   If any secret was accidentally staged or committed, untrack immediately:
   ```bash
   git rm --cached <sensitive_file>
   ```

### Environment Documentation
- If the project requires environment variables, maintain a `.env.example` file with dummy values and descriptive comments.
- Reference all required tokens in `README.md` or deployment documentation without embedding actual credentials.

---

## 4. Executing the Push

### Pushing Commits and Tags
When pushing commits that include version increments or tags:
```bash
git push --follow-tags <remote> <branch>
```

If setting up upstream tracking for the first time:
```bash
git push -u --follow-tags <remote> <branch>
```
