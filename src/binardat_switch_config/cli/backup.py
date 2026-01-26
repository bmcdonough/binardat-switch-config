"""Backup command implementation."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
import yaml

from ..exceptions import (
    ConfigRetrievalError,
    GitOperationError,
    NetmikoConnectionError,
    StorageError,
)
from ..netmiko.connection import SwitchConnection
from ..netmiko.retrieval import ConfigNormalizer, ConfigRetriever
from ..storage.filesystem import ConfigStorage
from ..storage.git_manager import GitManager

logger = logging.getLogger(__name__)


def load_inventory(inventory_path: Path) -> dict:
    """Load and parse inventory file.

    Args:
        inventory_path: Path to inventory.yaml

    Returns:
        Parsed inventory dictionary

    Raises:
        SystemExit: If inventory cannot be loaded
    """
    if not inventory_path.exists():
        click.echo(f"Error: Inventory file not found: {inventory_path}", err=True)
        sys.exit(1)

    try:
        with open(inventory_path) as f:
            inventory = yaml.safe_load(f)

        # Substitute environment variables
        inventory = substitute_env_vars(inventory)

        return inventory

    except yaml.YAMLError as e:
        click.echo(f"Error: Invalid YAML in inventory: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading inventory: {e}", err=True)
        sys.exit(1)


def substitute_env_vars(data: any) -> any:
    """Recursively substitute environment variables in data structure.

    Replaces ${VAR_NAME} with environment variable values.

    Args:
        data: Data structure (dict, list, str, etc.)

    Returns:
        Data with environment variables substituted
    """
    if isinstance(data, dict):
        return {k: substitute_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Replace ${VAR} with environment variable
        import re

        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(r"\$\{(\w+)\}", replace_var, data)
    else:
        return data


def get_switch_config(inventory: dict, switch_name: str) -> Optional[dict]:
    """Get configuration for a specific switch.

    Args:
        inventory: Parsed inventory dictionary
        switch_name: Name of switch to find

    Returns:
        Switch configuration dictionary, or None if not found
    """
    switches = inventory.get("switches", [])
    for switch in switches:
        if switch.get("name") == switch_name:
            # Merge with defaults
            defaults = inventory.get("defaults", {})
            config = {**defaults, **switch}
            return config

    return None


def backup_single_switch(
    switch_name: str,
    inventory: dict,
    storage: ConfigStorage,
    git_mgr: GitManager,
    dry_run: bool = False,
) -> bool:
    """Backup a single switch.

    Args:
        switch_name: Name of switch to backup
        inventory: Parsed inventory
        storage: ConfigStorage instance
        git_mgr: GitManager instance
        dry_run: Don't make changes if True

    Returns:
        True if successful, False otherwise
    """
    # Get switch config
    switch_config = get_switch_config(inventory, switch_name)
    if not switch_config:
        click.echo(f"Error: Switch '{switch_name}' not found in inventory", err=True)
        return False

    # Check if switch is enabled
    if not switch_config.get("enabled", True):
        click.echo(f"Skipping {switch_name} (disabled in inventory)")
        return True

    click.echo(f"\nBacking up {switch_name} ({switch_config['host']})...")

    try:
        # Connect to switch
        with SwitchConnection(
            host=switch_config["host"],
            device_type=switch_config.get("device_type", "cisco_ios"),
            username=switch_config["username"],
            password=switch_config.get("password"),
            key_file=switch_config.get("key_file"),
            port=switch_config.get("port", 22),
            timeout=switch_config.get("timeout", 30.0),
        ) as conn:
            click.echo("  ✓ Connected")

            # Retrieve configuration
            retriever = ConfigRetriever(conn)
            raw_config = retriever.retrieve_running_config()
            click.echo(f"  ✓ Retrieved running config ({len(raw_config)} bytes)")

            # Try to get startup config
            startup_config = retriever.retrieve_startup_config()
            if startup_config:
                click.echo(f"  ✓ Retrieved startup config ({len(startup_config)} bytes)")

        # Normalize configuration
        normalizer = ConfigNormalizer()
        normalized_config = normalizer.normalize(raw_config, switch_config.get("device_type", "cisco_ios"))

        if startup_config:
            normalized_startup = normalizer.normalize(startup_config, switch_config.get("device_type", "cisco_ios"))

        # Check for changes
        old_config = storage.load_config(switch_name, "running-config")
        has_changes = old_config is None or old_config != normalized_config

        if not has_changes:
            click.echo("  ✓ No changes detected")
            return True

        if dry_run:
            click.echo("  ! Changes detected (dry-run, not saving)")
            return True

        # Save to filesystem
        timestamp = datetime.now().isoformat()
        metadata = {
            "last_backup": timestamp,
            "host": switch_config["host"],
            "device_type": switch_config.get("device_type", "cisco_ios"),
        }

        config_file = storage.save_config(
            switch_name, "running-config", normalized_config, metadata
        )
        click.echo(f"  ✓ Saved running config")

        if startup_config:
            storage.save_config(switch_name, "startup-config", normalized_startup)
            click.echo(f"  ✓ Saved startup config")

        # Git operations
        files_to_add = [config_file]
        if startup_config:
            files_to_add.append(storage.get_switch_path(switch_name) / "startup-config.txt")
        files_to_add.append(storage.get_switch_path(switch_name) / "metadata.yaml")

        git_mgr.add_files(files_to_add)

        # Create commit message
        if old_config:
            old_lines = len(old_config.splitlines())
            new_lines = len(normalized_config.splitlines())
            diff_lines = new_lines - old_lines
            commit_msg = f"[{switch_name}] Configuration updated\n\n"
            commit_msg += f"Changes detected:\n"
            commit_msg += f"- running-config: {new_lines} lines ({diff_lines:+d})\n"
            if startup_config:
                commit_msg += f"- startup-config: updated\n"
            commit_msg += f"\nAutomated backup by binardat-switch-config"
        else:
            commit_msg = f"[{switch_name}] Initial backup\n\n"
            commit_msg += f"First backup of switch configuration\n"
            commit_msg += f"\nAutomated backup by binardat-switch-config"

        commit_sha = git_mgr.commit(commit_msg)
        if commit_sha:
            click.echo(f"  ✓ Created commit {commit_sha[:7]}")

            # Push if configured
            if switch_config.get("auto_push", True):
                try:
                    git_mgr.push()
                    click.echo(f"  ✓ Pushed to remote")
                except GitOperationError as e:
                    logger.warning(f"Failed to push: {e}")
                    click.echo(f"  ! Could not push to remote: {e}")

        click.echo(f"✓ Backup complete for {switch_name}")
        return True

    except NetmikoConnectionError as e:
        click.echo(f"  ✗ Connection failed: {e}", err=True)
        logger.error(f"Connection failed for {switch_name}: {e}")
        return False

    except ConfigRetrievalError as e:
        click.echo(f"  ✗ Config retrieval failed: {e}", err=True)
        logger.error(f"Config retrieval failed for {switch_name}: {e}")
        return False

    except (StorageError, GitOperationError) as e:
        click.echo(f"  ✗ Storage/Git error: {e}", err=True)
        logger.error(f"Storage/Git error for {switch_name}: {e}")
        return False

    except Exception as e:
        click.echo(f"  ✗ Unexpected error: {e}", err=True)
        logger.error(f"Unexpected error backing up {switch_name}: {e}", exc_info=True)
        return False


@click.command()
@click.argument("switch_name", required=False)
@click.option("--all", "backup_all", is_flag=True, help="Backup all enabled switches")
@click.option(
    "--tags",
    help="Comma-separated list of tags to filter switches (requires --all)",
)
@click.option("--dry-run", is_flag=True, help="Don't make changes, just show what would happen")
@click.option(
    "--inventory",
    type=click.Path(path_type=Path),
    help="Path to inventory file (default: <config-repo>/inventory.yaml)",
)
@click.pass_context
def backup(
    ctx: click.Context,
    switch_name: Optional[str],
    backup_all: bool,
    tags: Optional[str],
    dry_run: bool,
    inventory: Optional[Path],
) -> None:
    """Backup switch configuration(s).

    Examples:
        binardat-config backup switch-01
        binardat-config backup --all
        binardat-config backup --all --tags production,office
    """
    config_repo = ctx.obj["config_repo"]

    # Validate arguments
    if not switch_name and not backup_all:
        click.echo("Error: Must specify either SWITCH_NAME or --all", err=True)
        sys.exit(1)

    if switch_name and backup_all:
        click.echo("Error: Cannot specify both SWITCH_NAME and --all", err=True)
        sys.exit(1)

    if tags and not backup_all:
        click.echo("Error: --tags requires --all", err=True)
        sys.exit(1)

    # Load inventory
    inventory_path = inventory or (config_repo / "inventory.yaml")
    inv = load_inventory(inventory_path)

    # Initialize storage and git
    storage = ConfigStorage(config_repo)
    git_mgr = GitManager(config_repo)

    if dry_run:
        click.echo("=== DRY RUN MODE ===\n")

    # Backup switches
    if switch_name:
        # Single switch backup
        success = backup_single_switch(switch_name, inv, storage, git_mgr, dry_run)
        sys.exit(0 if success else 1)

    else:
        # Multiple switch backup
        switches = inv.get("switches", [])

        # Filter by tags if specified
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            switches = [
                s
                for s in switches
                if any(tag in s.get("tags", []) for tag in tag_list)
            ]
            click.echo(f"Filtered to {len(switches)} switches with tags: {', '.join(tag_list)}")

        # Filter enabled switches
        switches = [s for s in switches if s.get("enabled", True)]

        if not switches:
            click.echo("No enabled switches found in inventory")
            sys.exit(0)

        click.echo(f"Backing up {len(switches)} switches...\n")

        # Backup each switch
        results = []
        for switch in switches:
            success = backup_single_switch(
                switch["name"], inv, storage, git_mgr, dry_run
            )
            results.append((switch["name"], success))

        # Summary
        click.echo("\n" + "=" * 50)
        click.echo("BACKUP SUMMARY")
        click.echo("=" * 50)

        successful = sum(1 for _, success in results if success)
        failed = len(results) - successful

        click.echo(f"Total: {len(results)}")
        click.echo(f"Successful: {successful}")
        click.echo(f"Failed: {failed}")

        if failed > 0:
            click.echo("\nFailed switches:")
            for name, success in results:
                if not success:
                    click.echo(f"  - {name}")
            sys.exit(1)
        else:
            click.echo("\n✓ All backups completed successfully")
            sys.exit(0)
