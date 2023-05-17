"""Program arguments."""

from argparse import ArgumentParser
from functools import cache
from pathlib import Path
from typing import Optional


class Args:
    """Program arguments."""

    def __init__(self):
        self.profile_dir: Optional[Path] = None

    def parse_args(self, argv: Optional[list[str]] = None):
        parser = ArgumentParser()
        parser.add_argument(
            "-p",
            "--profile",
            help="Write profiling data to the specified directory",
            type=Path,
            dest="profile_dir",
        )
        parser.parse_args(argv, namespace=self)

    @property
    def is_profiling_enabled(self) -> bool:
        """Return True is profiling is enabled, otherwise False."""
        return self.profile_dir is not None


@cache
def get_args() -> Args:
    """Return the instance of Args."""
    return Args()
