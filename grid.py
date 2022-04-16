#!/usr/bin/env python3
from dataclasses import dataclass
import numpy as np
from numpy.typing import ArrayLike
from PIL import Image
import random
from typing import List, Dict, Tuple
import math
import json
import os


@dataclass()
class RGB:
    r: int
    g: int
    b: int

    def __init__(self, hex_represssentation: str):
        """ Creates an RGB value from a hex representation """
        self.r = int(hex_represssentation[:2], 16)
        self.g = int(hex_represssentation[2:4], 16)
        self.b = int(hex_represssentation[4:], 16)

    def to_np_array(self) -> ArrayLike:
        """ This is usefull when assigning color to bitmap """
        return np.array([self.r, self.g, self.b], dtype=np.uint8)


def colors_match(c1: ArrayLike, c2: ArrayLike) -> bool:
    """ Check that colors match """
    if c1[0] == c2[0] and c1[1] == c2[1] and c1[2] == c2[2]:
        return True
    else:
        return False


class Grid:
    """ Creates a grid """

    def __init__(
        self,
        gap: int,
        external_gap: int,
        square_width: int,
        square_height: int,
        colors: List[RGB],
        bg: RGB,
        width: int = 1920,
        height: int = 1080,
    ):
        """ Initializes the grid & checks that the gaps and sizes match """
        # 1. Check width & heihgt matches with the gaps & sizes
        if (width - 2 * external_gap + gap) % (square_width + gap) != 0:
            raise ValueError(
                f"Please give a square dimension, st: (width - 2 * external_gap + gap): {width - 2 * external_gap} + gap is divisible by (square_width + gap): {square_width} + gap "
            )
        if (height - 2 * external_gap + gap) % (square_height + gap) != 0:
            raise ValueError(
                f"Please give a square dimension, st: (height - 2 * external_gap + gap): {height - 2 * external_gap} + gap is divisible by (square_height + gap): {square_height} + gap "
            )

        self.square_width = square_width
        self.square_height = square_height
        self.gap = gap
        self.external_gap = external_gap

        self.colors = colors
        self.bg = bg

        # Compute the number of squares in the vertical and horizontal direction
        self.n_vertical = (height - 2 * external_gap + gap) // (square_height + gap)
        self.n_horizontal = (width - 2 * external_gap + gap) // (square_width + gap)

        self.squares = np.full(
            (self.n_vertical, self.n_horizontal, 3), bg.to_np_array()
        )  # Goes square, gap, square, gap, square ect.
        self.horizontal_gaps = np.full(
            (self.n_vertical - 1, self.n_horizontal, 3), bg.to_np_array()
        )
        self.vertical_gaps = np.full(
            (self.n_vertical, self.n_horizontal - 1, 3), bg.to_np_array()
        )
        self.middle_gaps = np.full(
            (self.n_vertical - 1, self.n_horizontal - 1, 3), bg.to_np_array()
        )

        # Give squares a randcom color
        for i in range(self.n_vertical):
            for j in range(self.n_horizontal):
                if colors_match(self.squares[i][j], self.bg.to_np_array()):
                    self.squares[i][j] = random.choice(self.colors).to_np_array()

    def chain_vertical(self):
        """ Chains the squares together in the horizontal direction """
        for i in range(self.n_vertical - 1):
            for j in range(self.n_horizontal):
                if colors_match(self.squares[i][j], self.squares[i + 1][j]):
                    self.horizontal_gaps[i][j] = self.squares[i][j]

    def chain_horizontal(self):
        """ Chains the squares together in the veritcal direction """
        for i in range(self.n_vertical):
            for j in range(self.n_horizontal - 1):
                if colors_match(self.squares[i][j], self.squares[i][j + 1]):
                    self.vertical_gaps[i][j] = self.squares[i][j]

    def chain_squares(self, with_middles: bool = False):
        """ Chains squares together if they share the samme color """
        self.chain_horizontal()
        self.chain_vertical()
        # Add middle gaps
        if with_middles:
            for i in range(self.n_vertical - 1):
                for j in range(self.n_horizontal - 1):
                    if (
                        colors_match(self.squares[i][j], self.squares[i][j + 1])
                        and colors_match(
                            self.squares[i + 1][j], self.squares[i + 1][j + 1]
                        )
                        and colors_match(self.squares[i][j], self.squares[i + 1][j])
                    ):
                        self.middle_gaps[i][j] = self.squares[i][j]

    def _add_squares(self, bitmap: ArrayLike) -> ArrayLike:
        """ Adds the squares to the bitmap """
        for i in range(self.n_vertical):
            for j in range(self.n_horizontal):
                # Get the color check the other colors
                color = self.squares[i][j]
                start_i, start_j = (
                    i * (self.square_height + self.gap) + self.external_gap,
                    j * (self.square_width + self.gap) + self.external_gap,
                )
                for idx in range(start_i, start_i + self.square_height):
                    for jdx in range(start_j, start_j + self.square_width):
                        bitmap[idx][jdx] = color

        return bitmap

    def _add_horizontal_gaps(self, bitmap: ArrayLike) -> ArrayLike:
        """ Adds the horizontal gaps to the bitmap """
        for i in range(self.n_vertical - 1):
            for j in range(self.n_horizontal):
                color = self.horizontal_gaps[i][j]
                start_i, start_j = (
                    i * (self.square_height + self.gap)
                    + self.external_gap
                    + self.square_height,
                    j * (self.square_width + self.gap) + self.external_gap,
                )
                for idx in range(start_i, start_i + self.gap):
                    for jdx in range(start_j, start_j + self.square_width):
                        bitmap[idx][jdx] = color

        return bitmap

    def _add_vertical_gaps(self, bitmap: ArrayLike) -> ArrayLike:
        """ Adds the vertical gaps to the bitmap """
        for i in range(self.n_vertical):
            for j in range(self.n_horizontal - 1):
                color = self.vertical_gaps[i][j]
                start_i, start_j = (
                    i * (self.square_height + self.gap) + self.external_gap,
                    j * (self.square_width + self.gap)
                    + self.external_gap
                    + self.square_width,
                )
                for idx in range(start_i, start_i + self.square_height):
                    for jdx in range(start_j, start_j + self.gap):
                        bitmap[idx][jdx] = color

        return bitmap

    def _add_middle_gaps(self, bitmap: ArrayLike) -> ArrayLike:
        """ Adds the vertical gaps to the bitmap """
        for i in range(self.n_vertical - 1):
            for j in range(self.n_horizontal - 1):
                color = self.middle_gaps[i][j]
                start_i, start_j = (
                    i * (self.square_height + self.gap)
                    + self.external_gap
                    + self.square_height,
                    j * (self.square_width + self.gap)
                    + self.external_gap
                    + self.square_width,
                )
                for idx in range(start_i, start_i + self.gap):
                    for jdx in range(start_j, start_j + self.gap):
                        bitmap[idx][jdx] = color

        return bitmap

    def create_image(self) -> ArrayLike:
        """ Creates the image """
        height = (
            self.n_vertical * (self.gap + self.square_height)
            - self.gap
            + 2 * self.external_gap
        )
        width = (
            self.n_horizontal * (self.gap + self.square_width)
            - self.gap
            + 2 * self.external_gap
        )

        bitmap = np.full((height, width, 3), self.bg.to_np_array(), dtype=np.uint8)
        return self._add_middle_gaps(
            self._add_horizontal_gaps(
                self._add_vertical_gaps(self._add_squares(bitmap))
            )
        )


if __name__ == "__main__":
    with open(os.path.join(os.getcwd(), "config.json"), "r") as file:
        cfg = json.load(file)
        grid = Grid(
            gap=cfg["internal-gap"],
            external_gap=cfg["external-gap"],
            square_width=cfg["square-width"],
            square_height=cfg["square-height"],
            bg=RGB(cfg["bg"]),
            colors=[RGB(c) for c in cfg["colors"]],
            width=cfg["width"],
            height=cfg["height"],
        )
        # chose one:
        choice = ""
        while choice not in ["1", "2", "3", "4", "q"]:
            choice = input(
                """Please chose an option for connecting squares with the same color:
                    \n  1. chain squares vertically.
                    \n  2. chain squares horizontally.
                    \n  3. chain squares vertically & horizontally.
                    \n  4. chain squares vertically & horizontally and fill out the middles.
                    \nChose (1-4), 'q' to quit: """
            )
        if choice == "q":
            exit()
        elif choice == "1":
            grid.chain_vertical()
        elif choice == "2":
            grid.chain_horizontal()
        elif choice == "3":
            grid.chain_squares()
        elif choice == "4":
            grid.chain_squares(with_middles=True)

        bitmap = grid.create_image()
        img = Image.fromarray(bitmap, "RGB")
        img.show()
