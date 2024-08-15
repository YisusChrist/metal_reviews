"""Main module for the package."""

from collections import OrderedDict
from pathlib import Path

from rich import print

from metal_reviews.report import get_albums_list, select_album_randomly_using_weights
from metal_reviews.utils import parse_markdown_file


def main() -> None:
    # Example usage
    file_path = Path("D:/Documents/notes/Metal albums.md")
    section_title = "REVIEW"

    data: OrderedDict[str, list[str]] = parse_markdown_file(file_path)
    albums: list[str] = get_albums_list(data[section_title])

    chosen_album, album_weight = select_album_randomly_using_weights(albums)

    print(f"Randomly selected album: {chosen_album}")
    print(f"Album weight: {album_weight}")


if __name__ == "__main__":
    main()
