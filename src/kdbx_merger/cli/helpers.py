import pathlib

from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
import questionary as q

from kdbx_merger.models import KeePassDBFile, MergeConfigFile


def create_kdbx_db_file(db_path: pathlib.Path) -> KeePassDBFile:
    if not db_path:
        raise ValueError(f"Invalid value provided for db_path. {db_path} received, a valid file path expected")
    if not db_path.is_file():
        raise ValueError(f"The database path received is not a file")
    if q.confirm(f"Does file {db_path} use password?").unsafe_ask():
        password = q.password("Enter the password").unsafe_ask()
    else:
        password = None
    if q.confirm(f"Does file {db_path} use a key file?").unsafe_ask():
        key_file = q.path(
            "Enter the path to the key file",
            validate=lambda p: pathlib.Path(p).exists() and pathlib.Path(p).is_file()
        ).unsafe_ask()
        key_file = pathlib.Path(key_file)
    else:
        key_file = None
    try:
        str_key_file = str(key_file) if key_file else None
        PyKeePass(str(db_path.absolute()), password=password, keyfile=str_key_file)
    except CredentialsError:
        if q.confirm("Could not open the file. Credentials mismatch. Want to try again?").unsafe_ask():
            return create_kdbx_db_file(db_path)
        else:
            raise
    return KeePassDBFile(db_file=db_path, password=password, key_file=key_file)
