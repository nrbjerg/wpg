# NOTE: the color rgb (0, 0, 0) black, dosn't work with this script
# /usr/bin/env python3
from config import WIDTH, HEIGHT, COLORS, RATIOS, POINTS_WITH_RANDOM_COLORS
from canvas import Canvas
import numpy as np
from typing import Callable, Dict, Tuple, List
from numpy.typing import ArrayLike
from tqdm import tqdm


# TODO: Maybe take inspiration from barnes hut and create quadrants.
def nearest_neighbour(
    canvas: Canvas,
    colored_points_and_color: Dict[Tuple[int], Tuple[int]],
    metric: Callable[ArrayLike, float],
) -> Canvas:
    """Perform the nearest neighbour algorithm."""
    points = list(colored_points_and_color.keys())
    for (y0, x0) in tqdm(canvas.pixels()):

        # Find the closest, color
        distances = [metric((y0 - y, x0 - x)) for (y, x) in points]
        closest_y, closest_x = points[np.argmin(distances)]

        canvas.set_pixel(y0, x0, canvas.get_color_of_pixel(closest_y, closest_x))

    return canvas


def main():
    """Run the script."""
    canvas = Canvas(WIDTH, HEIGHT)
    # Color random points

    total = sum(RATIOS)
    color_weights = [ratio / total for ratio in RATIOS]
    for _ in range(POINTS_WITH_RANDOM_COLORS):
        y, x = np.random.randint(0, HEIGHT - 1), np.random.randint(0, WIDTH - 1)
        color = COLORS[np.random.choice(range(0, len(COLORS)), p=color_weights)]

        canvas.set_pixel(y, x, color)

    # Figure out what points are colored.
    colored_points_and_colors = {}
    for (y, x) in canvas.pixels():
        if all(canvas.get_color_of_pixel(y, x) == (0, 0, 0)):
            continue
        else:
            colored_points_and_colors[(y, x)] = canvas.get_color_of_pixel(y, x)

    # Gives you loads of angles of 45 degrees.
    taxicab = lambda vec: sum(map(abs, vec))
    # Rounder corners.
    euclidian = lambda vec: np.sqrt(sum(map(lambda x: x ** 2, vec)))

    canvas = nearest_neighbour(canvas, colored_points_and_colors, euclidian)
    canvas.save("nearest_neighbour.jpeg")


if __name__ == "__main__":
    main()
