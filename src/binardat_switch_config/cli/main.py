"""Main CLI entry point for binardat-switch-config."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# Global options
@click.group()
@click.option(
    "--config-repo",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to configuration repository (default: current directory)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress all output except errors",
)
@click.pass_context
def cli(ctx: click.Context, config_repo: Optional[Path], verbose: bool, quiet: bool) -> None:
    """Network switch configuration management with netmiko.

    Backup, version control, and rollback configurations for network switches.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Set logging level
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Store config repo path in context
    if config_repo:
        ctx.obj["config_repo"] = config_repo
    else:
        ctx.obj["config_repo"] = Path.cwd()

    logger.debug(f"Using config repository: {ctx.obj['config_repo']}")


@cli.command()
@click.argument("path", type=click.Path(path_type=Path))
@click.pass_context
def init(ctx: click.Context, path: Path) -> None:
    """Initialize a new configuration repository.

    Creates directory structure and initializes git repository.

    Example:
        binardat-config init /var/lib/switch-configs
    """
    from ..storage.filesystem import ConfigStorage
    from ..storage.git_manager import GitManager

    try:
        path = path.resolve()
        click.echo(f"Initializing configuration repository at {path}")

        # Initialize storage
        storage = ConfigStorage(path)
        storage.initialize()
        click.echo("✓ Created directory structure")

        # Initialize git
        git_mgr = GitManager(path)
        git_mgr.initialize_repo()
        click.echo("✓ Initialized git repository")

        # Create sample inventory file
        inventory_path = path / "inventory.yaml"
        if not inventory_path.exists():
            sample_inventory = """# Switch Inventory Configuration
# See documentation for full options

defaults:
  username: admin
  password: ${SWITCH_PASSWORD}  # Environment variable
  port: 22
  timeout: 30.0
  device_type: cisco_ios

switches:
  - name: switch-example-01
    host: 192.168.1.10
    location: "Office Building A"
    enabled: false  # Disabled by default
    tags: [production, office]
"""
            inventory_path.write_text(sample_inventory)
            click.echo("✓ Created sample inventory.yaml")

        click.echo()
        click.echo(f"Configuration repository initialized at {path}")
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  1. Edit {inventory_path} to add your switches")
        click.echo("  2. Set environment variables for credentials")
        click.echo("  3. Run 'binardat-config backup <switch-name>' to test")

    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def validate_inventory(ctx: click.Context) -> None:
    """Validate inventory.yaml configuration.

    Checks syntax and connectivity information.
    """
    config_repo = ctx.obj["config_repo"]
    inventory_path = config_repo / "inventory.yaml"

    if not inventory_path.exists():
        click.echo(f"Error: inventory.yaml not found at {inventory_path}", err=True)
        sys.exit(1)

    try:
        import yaml

        with open(inventory_path) as f:
            inventory = yaml.safe_load(f)

        click.echo(f"✓ Valid YAML syntax")

        # Basic validation
        if "switches" not in inventory:
            click.echo("Warning: No 'switches' section found", err=True)
            sys.exit(1)

        switches = inventory["switches"]
        click.echo(f"✓ Found {len(switches)} switches in inventory")

        # Validate each switch
        for idx, switch in enumerate(switches):
            if "name" not in switch:
                click.echo(f"Error: Switch #{idx + 1} missing 'name' field", err=True)
                sys.exit(1)
            if "host" not in switch:
                click.echo(
                    f"Error: Switch '{switch['name']}' missing 'host' field", err=True
                )
                sys.exit(1)

        click.echo("✓ All switches have required fields")
        click.echo()
        click.echo("Inventory validation successful!")

    except yaml.YAMLError as e:
        click.echo(f"Error: Invalid YAML syntax: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Import and register subcommands
from .backup import backup

cli.add_command(backup)


def main() -> None:
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
