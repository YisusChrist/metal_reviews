"""Module to generate a random album from a list of albums and plot a histogram of the albums per band."""

import random
import re
from collections import Counter

import matplotlib.pyplot as plt


def get_albums_list(albums: list[str]) -> list[str]:
    # Remove the blank lines
    albums_list: list[str] = [album.strip() for album in albums if album]
    # Remove elements starting with - [x]
    albums_list = [album for album in albums_list if not re.match(r"- \[x\]", album)]
    # Remove the - [ ] from the beginning of each album
    albums_list = [re.sub(r"- \[ \] ", "", album) for album in albums_list]

    return albums_list


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
