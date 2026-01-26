"""Filesystem storage for switch configurations."""

import logging
from pathlib import Path
from typing import List, Optional

import yaml

from ..exceptions import StorageError

logger = logging.getLogger(__name__)


class ConfigStorage:
    """Manages configuration file storage on the filesystem.

    Directory structure:
        configs/
        ├── inventory.yaml
        └── switches/
            ├── switch-name-01/
            │   ├── running-config.txt
            │   ├── startup-config.txt
            │   └── metadata.yaml
            └── switch-name-02/
                └── ...
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize config storage.

        Args:
            base_path: Root directory for configuration storage
        """
        self.base_path = Path(base_path)
        self.switches_path = self.base_path / "switches"

    def initialize(self) -> None:
        """Initialize storage directory structure.

        Creates base directories if they don't exist.

        Raises:
            StorageError: If directory creation fails
        """
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.switches_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized storage at {self.base_path}")
        except Exception as e:
            logger.error(f"Failed to initialize storage at {self.base_path}: {e}")
            raise StorageError(f"Failed to initialize storage: {e}")

    def get_switch_path(self, switch_name: str) -> Path:
        """Get the storage path for a specific switch.

        Args:
            switch_name: Name of the switch

        Returns:
            Path to switch directory
        """
        return self.switches_path / switch_name

    def save_config(
        self,
        switch_name: str,
        config_type: str,
        config_data: str,
        metadata: Optional[dict] = None,
    ) -> Path:
        """Save configuration to filesystem.

        Args:
            switch_name: Name of the switch
            config_type: Type of config ('running-config', 'startup-config', etc.)
            config_data: Configuration content
            metadata: Optional metadata to save alongside config

        Returns:
            Path to the saved configuration file

        Raises:
            StorageError: If save operation fails
        """
        try:
            # Create switch directory if it doesn't exist
            switch_path = self.get_switch_path(switch_name)
            switch_path.mkdir(parents=True, exist_ok=True)

            # Save configuration file
            config_file = switch_path / f"{config_type}.txt"
            config_file.write_text(config_data, encoding="utf-8")
            logger.info(f"Saved {config_type} for {switch_name} to {config_file}")

            # Save metadata if provided
            if metadata:
                metadata_file = switch_path / "metadata.yaml"
                existing_metadata = {}
                if metadata_file.exists():
                    existing_metadata = yaml.safe_load(metadata_file.read_text())

                # Merge metadata
                existing_metadata.update(metadata)
                metadata_file.write_text(yaml.dump(existing_metadata), encoding="utf-8")
                logger.debug(f"Updated metadata for {switch_name}")

            return config_file

        except Exception as e:
            logger.error(f"Failed to save {config_type} for {switch_name}: {e}")
            raise StorageError(f"Failed to save config for {switch_name}: {e}")

    def load_config(self, switch_name: str, config_type: str) -> Optional[str]:
        """Load configuration from filesystem.

        Args:
            switch_name: Name of the switch
            config_type: Type of config to load

        Returns:
            Configuration content as string, or None if file doesn't exist

        Raises:
            StorageError: If load operation fails (but not if file doesn't exist)
        """
        try:
            config_file = self.get_switch_path(switch_name) / f"{config_type}.txt"

            if not config_file.exists():
                logger.debug(f"Config file does not exist: {config_file}")
                return None

            config_data = config_file.read_text(encoding="utf-8")
            logger.debug(f"Loaded {config_type} for {switch_name} ({len(config_data)} bytes)")
            return config_data

        except Exception as e:
            logger.error(f"Failed to load {config_type} for {switch_name}: {e}")
            raise StorageError(f"Failed to load config for {switch_name}: {e}")

    def config_exists(self, switch_name: str, config_type: str) -> bool:
        """Check if a configuration file exists.

        Args:
            switch_name: Name of the switch
            config_type: Type of config to check

        Returns:
            True if config file exists, False otherwise
        """
        config_file = self.get_switch_path(switch_name) / f"{config_type}.txt"
        return config_file.exists()

    def list_switches(self) -> List[str]:
        """List all switches with stored configurations.

        Returns:
            List of switch names

        Raises:
            StorageError: If listing fails
        """
        try:
            if not self.switches_path.exists():
                return []

            switches = [
                d.name
                for d in self.switches_path.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            switches.sort()
            return switches

        except Exception as e:
            logger.error(f"Failed to list switches: {e}")
            raise StorageError(f"Failed to list switches: {e}")

    def get_metadata(self, switch_name: str) -> dict:
        """Get metadata for a switch.

        Args:
            switch_name: Name of the switch

        Returns:
            Metadata dictionary (empty dict if no metadata exists)

        Raises:
            StorageError: If loading metadata fails
        """
        try:
            metadata_file = self.get_switch_path(switch_name) / "metadata.yaml"

            if not metadata_file.exists():
                return {}

            return yaml.safe_load(metadata_file.read_text()) or {}

        except Exception as e:
            logger.error(f"Failed to load metadata for {switch_name}: {e}")
            raise StorageError(f"Failed to load metadata for {switch_name}: {e}")

    def delete_switch(self, switch_name: str) -> None:
        """Delete all files for a switch.

        Args:
            switch_name: Name of the switch

        Raises:
            StorageError: If deletion fails
        """
        try:
            switch_path = self.get_switch_path(switch_name)

            if not switch_path.exists():
                logger.warning(f"Switch directory does not exist: {switch_path}")
                return

            # Delete all files in switch directory
            for file in switch_path.iterdir():
                file.unlink()

            # Remove directory
            switch_path.rmdir()
            logger.info(f"Deleted all files for switch {switch_name}")

        except Exception as e:
            logger.error(f"Failed to delete switch {switch_name}: {e}")
            raise StorageError(f"Failed to delete switch {switch_name}: {e}")
