import random
import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


def read_markdown_file(file_path: str | Path) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_section(markdown_content: str, section_title: str) -> str | None:
    # Create a regex pattern to find the section and its content
    pattern = rf"(## {section_title}\n(.*?)(?=\n### |\Z))"
    match = re.search(pattern, markdown_content, re.DOTALL)

    if match:
        return match.group(2).strip()
    else:
        return None


def get_albums_list(section_content: str) -> list[str]:
    albums: list[str] = section_content.split("\n")
    # Remove the blank lines
    albums = [album for album in albums if album]
    # Remove elements starting with - [x]
    albums = [album for album in albums if not re.match(r"- \[x\]", album)]
    # Remove the - [ ] from the beginning of each album
    albums = [re.sub(r"- \[ \] ", "", album) for album in albums]

    return albums


def select_album_randomly_using_weights(albums: list[str]) -> tuple[str, int]:
    # Step 1: Parse the albums and count the albums per band
    bands: list = []
    for album in albums:
        parts: list[str] = album.split(" - ")
        band: str = parts[2] if len(parts) == 3 else parts[2].split(" & ")[0]
        bands.append(band)

    band_counts = Counter(bands)

    # Step 2: Create a weighted list of albums
    weighted_albums: list[tuple[str, int]] = [
        (
            album,
            band_counts[
                (
                    album.split(" - ")[2]
                    if len(album.split(" - ")) == 3
                    else album.split(" - ")[2].split(" & ")[0]
                )
            ],
        )
        for album in albums
    ]

    # Step 3: Use random.choices to select a random album based on weights
    chosen_album: str = random.choices(
        population=[album for album, _ in weighted_albums],
        weights=[weight for _, weight in weighted_albums],
        k=1,
    )[0]

    return chosen_album, band_counts[chosen_album.split(" - ")[2]]


def select_album_randomly(albums: list[str]) -> tuple[str, int]:
    return random.choice(albums), 1


def plot_album_histogram(albums: list[str]) -> None:
    # Count the number of albums per band
    bands: list = []
    for album in albums:
        parts: list[str] = album.split(" - ")
        band: str = parts[2] if len(parts) == 3 else parts[2].split(" & ")[0]
        bands.append(band)
    band_counts = Counter(bands)

    # Sort the bands by count
    sorted_band_counts = reversed(
        sorted(band_counts.items(), key=lambda item: item[1], reverse=True)
    )
    sorted_bands, sorted_counts = zip(*sorted_band_counts)

    plt.figure(figsize=(10, 5))
    plt.barh(sorted_bands, sorted_counts, color="skyblue")
    plt.xlabel("Number of Albums")
    plt.ylabel("Bands")
    plt.title("Number of Albums per Band")
    plt.show()


def main() -> None:
    # Example usage
    file_path = "D:/Documents/notes/Metal albums.md"
    section_title = "REVIEW"

    markdown_content: str = read_markdown_file(file_path)
    section_content: str | None = extract_section(markdown_content, section_title)
    if not section_content:
        print(f"Section '{section_title}' not found in the markdown file.")
        return

    albums: list[str] = get_albums_list(section_content)
    chosen_album, album_weight = select_album_randomly_using_weights(albums)

    print(f"Randomly selected album: {chosen_album}")
    print(f"Album weight: {album_weight}")


if __name__ == "__main__":
    main()
