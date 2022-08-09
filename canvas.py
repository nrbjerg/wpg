#!/usr/bin/env python3
from typing import Iterable, Tuple, List, Union
from PIL import Image
from config import HEIGHT, WIDTH
import numpy as np
from numpy.typing import ArrayLike


def adjecent_pixels(y: int, x: int) -> Iterable[Tuple[int]]:
    """Iterate over the adjecent pixels."""
    if y != 0:
        yield (y - 1, x)
    if x != 0:
        yield (y, x - 1)

    if y != HEIGHT - 1:
        yield (y + 1, x)
    if x != WIDTH - 1:
        yield (y, x + 1)


class Canvas:
    """Model a canvas."""

    def pixels(self) -> Iterable[Tuple[int]]:
        """Iterate over the pixels."""
        for y in range(self.height):
            for x in range(self.width):
                yield (y, x)

    def adjecent_pixels(self, y: int, x: int) -> Iterable[Tuple[int]]:
        """Iterate over the adjecent pixels."""
        if y != 0:
            yield (y - 1, x)
        if x != 0:
            yield (y, x - 1)

        if y != self.height - 1:
            yield (y + 1, x)
        if x != self.width - 1:
            yield (y, x + 1)

    def __init__(self, width: int, height: int, is_rgb: bool = True):
        """Initialize canvas."""
        self.width = width
        self.height = height
        self.is_rgb = is_rgb
        self.tensor = np.zeros((height, width, 3 if self.is_rgb else 1), dtype="uint8")

    def set_pixel(self, y: int, x: int, color: Union[Tuple[int], int]):
        """Set the value of the pixel."""
        if self.is_rgb is True and type(color) is int:
            raise ValueError("Expected rgb value got grayscale.")
        elif self.is_rgb is False and type(color) is tuple:
            raise ValueError("Expected grayscale value got rgb.")

        self.tensor[y][x] = color

    def get_color_of_pixel(self, y: int, x: int) -> Union[Tuple[int], int]:
        """Get the color of a given pixel."""
        return self.tensor[y][x]

    def save(self, file_path: str):
        """Save the canvas to a file."""
        img = Image.fromarray(self.tensor)
        img.save(file_path)


def scale_up_by(canvas: Canvas, scale: int) -> Canvas:
    """Scales up the image, on the canvas, and returns it as a new canvas"""
    new = Canvas(canvas.width * scale, canvas.height * scale, canvas.is_rgb)

    for (y0, x0) in canvas.pixels():
        # Color blocks
        color = canvas.get_color_of_pixel(y0, x0)
        for y in range(scale * y0, scale * (y0 + 1)):
            for x in range(scale * x0, scale * (x0 + 1)):
                new.set_pixel(y, x, color)

    return new
