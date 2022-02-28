"""Program arguments."""

from argparse import ArgumentParser
from functools import cache
from pathlib import Path
from typing import Optional


class Args:
    """Program arguments."""

    def __init__(self):
        self.profile_dir: Optional[Path] = None
        self.parse_args()

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument(
            "-p",
            "--profile",
            help="Write profiling data to the specified directory",
            type=Path,
            dest="profile_dir",
        )
        parser.parse_args(namespace=self)

    @property
    def is_profiling_enabled(self) -> bool:
        """Return True is profiling is enabled, otherwise False."""
        return self.profile_dir is not None


@cache
def get_args() -> Args:
    """Return the instance of Args."""
    return Args()
