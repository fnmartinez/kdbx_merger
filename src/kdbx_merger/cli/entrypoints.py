import json
import pathlib

import click
import questionary

from kdbx_merger.cli import helpers
from kdbx_merger.models import MergeConfigFile


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--directory",
    "-d",
    type=click.types.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path),
    default=pathlib.Path("."),
    help="Path where all the .kdbx files are",
    show_default=True,
)
@click.option(
    "--trunk-file",
    "-t",
    type=click.types.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="File to use as trunk/cannon to merge all the others to",
)
@click.option(
    "--output",
    "-o",
    type=click.types.Path(exists=False, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    default=pathlib.Path(".") / "merge_config.json",
    help="",
)
def create_config(directory: pathlib.Path, trunk_file: pathlib.Path, output: pathlib.Path):
    if trunk_file:
        config_file = MergeConfigFile(trunk_file=helpers.create_kdbx_db_file(trunk_file))
    else:
        config_file = None
    kdbx_dbs = set()
    for kdbx_file in directory.glob("*.kdbx"):
        if questionary.confirm(f"Do you wish to merge {kdbx_file}?").unsafe_ask():
            kdbx_dbs.add(helpers.create_kdbx_db_file(kdbx_file))
    if not config_file:
        trunk_file = questionary.select(
            "Please, select the trunk file against which to merge all other files",
            choices=[questionary.Choice(title=str(db.db_file), value=db)
                     for db in kdbx_dbs]
        ).unsafe_ask()
        config_file = MergeConfigFile(trunk_file=trunk_file)
    if trunk_file in kdbx_dbs:
        kdbx_dbs.remove(trunk_file)
    config_file.other_files.update(kdbx_dbs)
    json.dump(config_file.to_dict(), output.open("w+"))


@click.command()
def merge():
    pass


cli.add_command(create_config)
cli.add_command(merge)
