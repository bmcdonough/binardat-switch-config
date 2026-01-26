"""Git operations for switch configuration version control."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import git
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from ..exceptions import GitOperationError

logger = logging.getLogger(__name__)


class GitManager:
    """Manages git operations for configuration version control.

    Example:
        >>> git_mgr = GitManager("/path/to/configs")
        >>> git_mgr.initialize_repo()
        >>> git_mgr.add_files([Path("switches/switch-01/running-config.txt")])
        >>> commit_sha = git_mgr.commit("Updated switch-01 config")
        >>> git_mgr.push()
    """

    def __init__(self, repo_path: Path) -> None:
        """Initialize git manager.

        Args:
            repo_path: Path to git repository root
        """
        self.repo_path = Path(repo_path)
        self._repo: Optional[Repo] = None

    @property
    def repo(self) -> Repo:
        """Get git repository object.

        Returns:
            GitPython Repo object

        Raises:
            GitOperationError: If repository is not initialized
        """
        if self._repo is None:
            try:
                self._repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                raise GitOperationError(
                    f"Not a git repository: {self.repo_path}. Run initialize_repo() first."
                )
        return self._repo

    def initialize_repo(self, initial_commit: bool = True) -> None:
        """Initialize a new git repository.

        Args:
            initial_commit: Create initial commit with .gitignore (default: True)

        Raises:
            GitOperationError: If initialization fails
        """
        try:
            if self.repo_path.exists() and (self.repo_path / ".git").exists():
                logger.info(f"Git repository already exists at {self.repo_path}")
                self._repo = Repo(self.repo_path)
                return

            # Create directory if it doesn't exist
            self.repo_path.mkdir(parents=True, exist_ok=True)

            # Initialize git repo
            self._repo = Repo.init(self.repo_path)
            logger.info(f"Initialized git repository at {self.repo_path}")

            if initial_commit:
                # Create .gitignore
                gitignore_path = self.repo_path / ".gitignore"
                gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local config
*.local
.env
"""
                gitignore_path.write_text(gitignore_content)

                # Create initial commit
                self._repo.index.add([".gitignore"])
                self._repo.index.commit("Initial commit")
                logger.info("Created initial commit")

        except Exception as e:
            logger.error(f"Failed to initialize git repository: {e}")
            raise GitOperationError(f"Failed to initialize repository: {e}")

    def add_files(self, files: List[Path]) -> None:
        """Stage files for commit.

        Args:
            files: List of file paths to stage (relative to repo root)

        Raises:
            GitOperationError: If staging fails
        """
        try:
            # Convert to relative paths
            relative_paths = []
            for file_path in files:
                if file_path.is_absolute():
                    relative_path = file_path.relative_to(self.repo_path)
                else:
                    relative_path = file_path
                relative_paths.append(str(relative_path))

            self.repo.index.add(relative_paths)
            logger.debug(f"Staged {len(relative_paths)} files")

        except Exception as e:
            logger.error(f"Failed to stage files: {e}")
            raise GitOperationError(f"Failed to stage files: {e}")

    def commit(self, message: str, author_name: Optional[str] = None,
               author_email: Optional[str] = None) -> Optional[str]:
        """Create a git commit.

        Args:
            message: Commit message
            author_name: Optional author name (uses git config if not provided)
            author_email: Optional author email (uses git config if not provided)

        Returns:
            Commit SHA hash, or None if nothing to commit

        Raises:
            GitOperationError: If commit fails
        """
        try:
            # Check if there are changes to commit
            if not self.has_changes():
                logger.info("No changes to commit")
                return None

            # Set author if provided
            if author_name and author_email:
                author = git.Actor(author_name, author_email)
                commit = self.repo.index.commit(message, author=author)
            else:
                commit = self.repo.index.commit(message)

            commit_sha = commit.hexsha
            logger.info(f"Created commit {commit_sha[:7]}: {message.splitlines()[0]}")
            return commit_sha

        except Exception as e:
            logger.error(f"Failed to create commit: {e}")
            raise GitOperationError(f"Failed to create commit: {e}")

    def push(self, remote: str = "origin", branch: Optional[str] = None) -> None:
        """Push commits to remote repository.

        Args:
            remote: Remote name (default: 'origin')
            branch: Branch name (default: current branch)

        Raises:
            GitOperationError: If push fails or remote doesn't exist
        """
        try:
            # Check if remote exists
            if remote not in [r.name for r in self.repo.remotes]:
                raise GitOperationError(
                    f"Remote '{remote}' not found. Add it with: "
                    f"git remote add {remote} <url>"
                )

            # Get current branch if not specified
            if branch is None:
                branch = self.repo.active_branch.name

            # Push to remote
            remote_obj = self.repo.remote(remote)
            logger.info(f"Pushing to {remote}/{branch}...")
            push_info = remote_obj.push(branch)

            # Check for errors
            for info in push_info:
                if info.flags & info.ERROR:
                    raise GitOperationError(f"Push failed: {info.summary}")

            logger.info(f"Successfully pushed to {remote}/{branch}")

        except GitOperationError:
            raise
        except Exception as e:
            logger.error(f"Failed to push to {remote}/{branch}: {e}")
            raise GitOperationError(f"Failed to push: {e}")

    def has_changes(self) -> bool:
        """Check if there are uncommitted changes.

        Returns:
            True if there are changes (staged or unstaged), False otherwise
        """
        try:
            # Check for staged changes
            staged_diff = self.repo.index.diff("HEAD")
            if len(staged_diff) > 0:
                return True

            # Check for unstaged changes
            unstaged_diff = self.repo.index.diff(None)
            if len(unstaged_diff) > 0:
                return True

            # Check for untracked files that are staged
            if self.repo.untracked_files:
                return True

            return False

        except Exception:
            # If HEAD doesn't exist (no commits yet), check if index has entries
            return len(self.repo.index.entries) > 0

    def get_file_at_commit(self, file_path: Path, commit_sha: str) -> str:
        """Retrieve file content at a specific commit.

        Args:
            file_path: Path to file (relative to repo root)
            commit_sha: Git commit SHA

        Returns:
            File content as string

        Raises:
            GitOperationError: If file retrieval fails
        """
        try:
            commit = self.repo.commit(commit_sha)

            # Convert to relative path if absolute
            if file_path.is_absolute():
                relative_path = file_path.relative_to(self.repo_path)
            else:
                relative_path = file_path

            # Get file content from commit
            blob = commit.tree / str(relative_path)
            content = blob.data_stream.read().decode("utf-8")

            logger.debug(
                f"Retrieved {relative_path} from commit {commit_sha[:7]} ({len(content)} bytes)"
            )
            return content

        except KeyError:
            raise GitOperationError(
                f"File {file_path} not found in commit {commit_sha[:7]}"
            )
        except Exception as e:
            logger.error(f"Failed to get file from commit: {e}")
            raise GitOperationError(f"Failed to get file from commit {commit_sha[:7]}: {e}")

    def list_commits(self, file_path: Optional[Path] = None, max_count: int = 50) -> List[Dict]:
        """List recent commits.

        Args:
            file_path: Optional file path to filter commits (relative to repo root)
            max_count: Maximum number of commits to return

        Returns:
            List of commit dictionaries with 'sha', 'message', 'author', 'date'

        Raises:
            GitOperationError: If listing commits fails
        """
        try:
            # Get commits
            if file_path:
                if file_path.is_absolute():
                    file_path = file_path.relative_to(self.repo_path)
                commits = list(self.repo.iter_commits(paths=str(file_path), max_count=max_count))
            else:
                commits = list(self.repo.iter_commits(max_count=max_count))

            result = []
            for commit in commits:
                result.append({
                    "sha": commit.hexsha,
                    "short_sha": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                })

            logger.debug(f"Listed {len(result)} commits")
            return result

        except Exception as e:
            logger.error(f"Failed to list commits: {e}")
            raise GitOperationError(f"Failed to list commits: {e}")

    def get_current_commit(self) -> Optional[str]:
        """Get current commit SHA.

        Returns:
            Current commit SHA, or None if no commits exist

        Raises:
            GitOperationError: If operation fails
        """
        try:
            if not self.repo.head.is_valid():
                return None
            return self.repo.head.commit.hexsha
        except Exception as e:
            logger.error(f"Failed to get current commit: {e}")
            raise GitOperationError(f"Failed to get current commit: {e}")

    def get_diff(self, old_commit: str, new_commit: str = "HEAD") -> str:
        """Get diff between two commits.

        Args:
            old_commit: Old commit SHA
            new_commit: New commit SHA (default: HEAD)

        Returns:
            Diff as string

        Raises:
            GitOperationError: If diff fails
        """
        try:
            old = self.repo.commit(old_commit)
            new = self.repo.commit(new_commit)

            diff = old.diff(new, create_patch=True)
            diff_text = "\n".join([str(d) for d in diff])

            return diff_text

        except Exception as e:
            logger.error(f"Failed to get diff: {e}")
            raise GitOperationError(f"Failed to get diff: {e}")
