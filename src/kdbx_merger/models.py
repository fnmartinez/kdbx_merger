from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Dict


@dataclass
class KeePassDBFile:
    db_file: Path
    password: str = None
    key_file: Path = None

    def __post_init__(self):
        if not self.db_file.exists():
            raise ValueError(f"The db file at {self.db_file} does not exist or is not readable")
        if not self.db_file.is_file():
            raise ValueError(f"The db file at {self.db_file} is not a file")
        if self.key_file:
            if not self.key_file.exists():
                raise ValueError(f"The key file at {self.key_file} does not exist or is not readable    ")
            if not self.key_file.is_file():
                raise ValueError(f"The key file at {self.key_file} is not a file")

    def to_dict(self) -> Dict:
        return {
            "db_file": self.db_file.absolute(),
            "password": self.password,
            "key_file": self.key_file.absolute()
        }


@dataclass
class MergeConfigFile:
    trunk_file: KeePassDBFile
    other_files: Set[KeePassDBFile] = field(default_factory=set)

    def to_dict(self) -> Dict:
        return {
            "trunk_file": self.trunk_file.to_dict(),
            "rest_files": [kdbxf.to_dict() for kdbxf in self.other_files]
        }
