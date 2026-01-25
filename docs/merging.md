# Merging Workflow

This document describes the workflow for contributing changes to this repository.

## Overview

All changes must follow this process:
1. Create an issue describing the change
2. Create a branch from that issue
3. Make your changes and commit them
4. Create a pull request
5. Merge after review and CI passes

## Step-by-Step Instructions

### 1. Create an Issue

Before starting work, create an issue on GitHub:

1. Go to the repository on GitHub
2. Click **Issues** → **New Issue**
3. Provide a clear title describing the change
4. Add a detailed description including:
   - What needs to be done
   - Why it's needed
   - Any relevant context or requirements
5. Add appropriate labels (e.g., `bug`, `enhancement`, `documentation`)
6. Click **Submit new issue**
7. Note the issue number (e.g., `#42`)

### 2. Create a Branch from the Issue

Create a branch with a descriptive name that references the issue:

```bash
# Fetch latest changes
git fetch origin
git checkout main
git pull origin main

# Create and checkout a new branch
# Format: issue-<number>-brief-description
git checkout -b issue-42-add-ssh-support
```

**Branch naming conventions:**
- `issue-<number>-<brief-description>` - For features and fixes
- `hotfix-<brief-description>` - For urgent production fixes
- `docs-<brief-description>` - For documentation-only changes

### 3. Make Your Changes

Work on your changes following the project's coding standards:

```bash
# Make your code changes
# ...

# Run linting and tests locally
black .
isort .
flake8 .
mypy .
pytest

# Run pre-commit hooks
pre-commit run --all-files
```

### 4. Commit Your Changes

Create meaningful commits with clear messages:

```bash
# Stage your changes
git add <files>

# Commit with a descriptive message
# Format: "<verb> <what> (#<issue>)"
git commit -m "Add SSH connection support (#42)"

# If you have multiple logical changes, make multiple commits
git commit -m "Add SSH connection class (#42)"
git commit -m "Add SSH authentication methods (#42)"
git commit -m "Add SSH connection tests (#42)"
```

**Commit message guidelines:**
- Use imperative mood ("Add feature" not "Added feature")
- Reference the issue number
- Keep the first line under 50 characters
- Add detailed description after a blank line if needed

### 5. Push Your Branch

Push your branch to GitHub:

```bash
git push -u origin issue-42-add-ssh-support
```

### 6. Create a Pull Request

1. Go to the repository on GitHub
2. Click **Pull requests** → **New pull request**
3. Select your branch as the compare branch
4. Fill in the PR template:
   - **Title:** Clear, descriptive title
   - **Description:**
     - Link to the issue (e.g., "Closes #42")
     - Summary of changes
     - Testing performed
     - Any breaking changes or special notes
5. Request reviewers if needed
6. Click **Create pull request**

### 7. Address Review Feedback

If reviewers request changes:

```bash
# Make the requested changes
# ...

# Commit and push
git add <files>
git commit -m "Address review feedback: update error handling (#42)"
git push
```

The pull request will automatically update with your new commits.

### 8. Merge the Pull Request

Once the PR is approved and CI passes:

1. Ensure all checks are green ✓
2. Ensure there are no merge conflicts
3. Click **Squash and merge** (preferred) or **Merge pull request**
4. Edit the commit message if needed
5. Click **Confirm merge**
6. Delete the branch after merging

### 9. Update Your Local Repository

After the PR is merged:

```bash
# Switch back to main
git checkout main

# Pull the latest changes
git pull origin main

# Delete your local branch
git branch -d issue-42-add-ssh-support
```

## Quick Example

Here's a complete example workflow:

```bash
# 1. Someone creates issue #42: "Add SSH support for switch connections"

# 2. Create and checkout branch
git checkout main
git pull origin main
git checkout -b issue-42-add-ssh-support

# 3. Make changes
# ... edit files ...

# 4. Test changes
black .
isort .
flake8 .
mypy .
pytest

# 5. Commit changes
git add src/connection.py tests/test_connection.py
git commit -m "Add SSH connection support (#42)"

# 6. Push branch
git push -u origin issue-42-add-ssh-support

# 7. Create PR on GitHub
# - Go to GitHub
# - Click "Compare & pull request"
# - Fill in description: "Closes #42"
# - Submit PR

# 8. After approval and CI passes, merge on GitHub

# 9. Clean up locally
git checkout main
git pull origin main
git branch -d issue-42-add-ssh-support
```

## Best Practices

- **Keep branches focused:** One issue per branch
- **Keep PRs small:** Easier to review and merge
- **Update frequently:** Rebase or merge main into your branch regularly
- **Test locally:** Run all linting and tests before pushing
- **Write good commit messages:** Future you will thank you
- **Link issues:** Always reference the issue number in commits and PRs
- **Review your own PR:** Check the diff on GitHub before requesting review

## Handling Merge Conflicts

If your branch has conflicts with main:

```bash
# Option 1: Rebase (cleaner history)
git checkout issue-42-add-ssh-support
git fetch origin
git rebase origin/main
# Resolve conflicts
git add <resolved-files>
git rebase --continue
git push --force-with-lease

# Option 2: Merge (safer)
git checkout issue-42-add-ssh-support
git fetch origin
git merge origin/main
# Resolve conflicts
git add <resolved-files>
git commit
git push
```

## Squashing Commits

If you have many small commits, you may want to squash them before merging:

```bash
# Interactive rebase to squash commits
git rebase -i HEAD~3  # For last 3 commits

# In the editor, change 'pick' to 'squash' or 's' for commits to combine
# Save and close the editor
# Edit the combined commit message
# Force push
git push --force-with-lease
```

Alternatively, use GitHub's "Squash and merge" button when merging the PR.
