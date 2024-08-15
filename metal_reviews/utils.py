"""Utility functions for the package."""

from collections import OrderedDict
from pathlib import Path
from typing import Any, Literal

import enmet  # type: ignore
import markdown_to_json  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from fake_useragent import FakeUserAgent  # type: ignore
from requests_cache import CachedSession
from rich import print
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

ua: FakeUserAgent = FakeUserAgent()


def send_request(album: str, band: str, year: str = "") -> list[Any | enmet.Album]:
    print(f"Searching for album '{album}' by '{band}'...")
    year_search: int | None = int(year) if year else None

    results: list[Any | enmet.Album] = enmet.search_albums(
        name=album,
        band=band,
        year_from=year_search,
        year_to=year_search,
        release_types=[type for type in enmet.ReleaseTypes],
    )
    return results


def search_album(year: str, album: str, band: str) -> list[Any | enmet.Album]:
    results: list[Any | enmet.Album] = send_request(album, band, year)
    if not results:
        # print("No results found, retrying with different search terms...")
        band_names: list = band.split(" & ")
        if len(band_names) == 1:
            band_names = band.split(" / ")
        if len(band_names) == 1:
            band_names = band.split(" - ")
        if len(band_names) > 1:
            for band_name in band_names:
                results = send_request(album, band_name, year)
                if results:
                    break
        if not results:
            results = send_request(album, band)

    # print(results)
    return results


def add_album(
    albums: list,
    album: enmet.Album,
    album_url: str,
    band_url: str,
    prefix: str,
) -> None:
    # print(f"[green]Adding album '{album.name}' by '{album.bands}'[/]")

    bands: str = " & ".join([band.name for band in album.bands])
    entry: str = (
        f"- {prefix}] {album.year} - [{album.name}]({album_url}) - [{bands}]({band_url})"
    )
    # print(f"[green]Entry: {entry}[/]")
    albums.append(entry)


def retrieve_url(type: Literal["bands", "albums"], type_id: str | int) -> str:
    if type == "bands":
        url: str = f"https://www.metal-archives.com/{type}/_/{type_id}"
    elif type == "albums":
        url = f"https://www.metal-archives.com/{type}/_/_/{type_id}"
    else:
        raise ValueError(f"Invalid type '{type}'")

    response = CachedSession().get(url, headers={"User-Agent": ua.random})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    html_tag: str = f"{type[:-1]}_name"
    type_url = soup.find("h1", {"class": html_tag})
    if type_url:
        return type_url.find("a")["href"]

    return ""


def save_result(result: dict, albums_file: Path) -> None:
    # Get the albums_file name and extension
    file_name: str = albums_file.stem
    file_extension: str = albums_file.suffix

    # Create a new file name
    new_file: Path = albums_file.with_name(f"{file_name}_new{file_extension}").resolve()

    with new_file.open("w", encoding="utf-8") as file:
        for type, entries in result.items():
            file.write(f"# {type}\n")
            for entry in entries:
                file.write(f"{entry}\n")
            file.write("\n")


def parse_markdown_file(albums_file) -> OrderedDict[str, list[str]]:
    text: str = albums_file.read_text(encoding="utf-8")
    return markdown_to_json.dictify(text)


def print_dict(data: dict, sep="") -> None:
    if not data:
        print("No data found")

    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{sep}{key}:")
            print_dict(value, sep + " ")
        elif isinstance(value, list):
            print(f"{sep}{key}:")
            for item in value:
                print(f"{sep} - {item}")
        else:
            print(f"{sep}{key}: {value}")


def update_albums_file(albums_file: str | Path) -> None:
    albums_file = Path(albums_file).resolve()
    albums: OrderedDict[str, list[str]] = parse_markdown_file(albums_file)

    result: dict = {}

    # Calculate the total number of items to process
    total_items: int = sum(len(entries) for entries in albums.values())

    # Setup rich progress bar
    progress = Progress(
        TextColumn("Processing albums..."),
        BarColumn(),
        TaskProgressColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TimeRemainingColumn(),
    )

    with progress:
        task = progress.add_task("Processing", total=total_items)

        for type, entries in albums.items():
            result[type] = []
            for entry in entries:
                if "https://www.metal-archives.com/albums/" in entry:
                    result[type].append(entry)
                    continue

                prefix, data = entry.split("] ", 1)
                year, album, band = data.split(" - ", 2)

                results: list[enmet.Album] = search_album(year, album, band)
                if not results:
                    print(f"[red]No results found for '{album}' by '{band}'[/]")
                    result[type].append(entry)
                elif len(results) > 1:
                    print(
                        f"[yellow]Multiple results found for '{album}' by '{band}'[/]"
                    )
                    result[type].append(entry)
                else:
                    band_url: str = retrieve_url("bands", results[0].bands[0].id)
                    album_url: str = retrieve_url("albums", results[0].id)
                    add_album(result[type], results[0], album_url, band_url, prefix)

                # Update progress bar after each entry is processed
                progress.update(task, advance=1)

    save_result(result, albums_file)
