import os
import sys
from typing import Tuple

import click

from main_file_processor import process_file


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--black-list", "-b", multiple=True, default=None,
    help="Classes to censor (e.g. --black-list cigarette --black-list MALE_GENITALIA_EXPOSED)"
)
@click.option(
    "--pixelation/--no-pixelation", default=True,
    help="Pixelate or draw bounding boxes."
)
def main(
        input_path: str,
        black_list: Tuple[str, ...],
        pixelation: bool,
) -> None:
    """
    Parse the input media and apply censorship.
    """
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    print(f"Censoring end {process_file(input_path, list(black_list), pixelation)}")


if __name__ == "__main__":
    main()
