#!/usr/bin/env python3
from typing import Tuple, List, Iterable, Dict
from dataclasses import dataclass
import numpy as np
import random
from numpy.typing import ArrayLike
from tqdm import trange, tqdm
from copy import deepcopy
from canvas import Canvas, adjecent_pixels, scale_up_by
from config import (
    COLORS,
    RATIOS,
    WIDTH,
    HEIGHT,
    PROBABILITY_FOR_COLOR_TO_STAY_THE_SAME,
    NUMBER_OF_STEPS,
    SCALE,
    PASSES_REMOVING_NOISE,
)


def random_walk(canvas: Canvas) -> Canvas:
    """Perform a random walk on the canvas."""
    pos = [np.random.randint(0, canvas.height), np.random.randint(0, canvas.width)]
    color = list(COLORS[0])
    total = sum(RATIOS)
    weights = [ratio / total for ratio in RATIOS]

    for _ in trange(0, NUMBER_OF_STEPS):
        canvas.set_pixel(pos[0], pos[1], color)

        # Update position and color
        pos[np.random.randint(0, len(pos))] += 1 if np.random.rand() > 0.5 else -1

        if np.random.rand() > PROBABILITY_FOR_COLOR_TO_STAY_THE_SAME:
            # Pick a new color according to the ratios
            color = list(COLORS[np.random.choice(range(0, len(COLORS)), p=weights)])

        # Boundary checks
        constrain = lambda x, M, m: x if x >= m and x < M else (M if x < M else m)
        pos[0] = constrain(pos[0], canvas.height - 1, 0)
        pos[1] = constrain(pos[1], canvas.width - 1, 0)

    return canvas


# NOTE: I dont think this needs to be recursive (it scans from top to bottom, left to right.)
def remove_black_pixels(canvas: Canvas, depth: int = 0, max_depth: int = 6) -> Canvas:
    """Remove the black colored pixels, by replacing them with the color adjecent to them."""
    if depth == max_depth:
        return canvas

    count = 0
    for (y0, x0) in canvas.pixels():
        if all(canvas.get_color_of_pixel(y0, x0) == np.zeros(3, dtype="uint8")):

            # Pick the color of the neighbours, randomly but with probability proprotional to the ratio.
            neighbour_colors = [
                tuple(canvas.get_color_of_pixel(y, x))
                for (y, x) in adjecent_pixels(y0, x0)
            ]
            color_ratios = {
                color: neighbour_colors.count(color)
                for color in {tuple(c) for c in neighbour_colors}
                if sum(color) != 0
            }

            colors = list(color_ratios.keys())
            if (
                len(colors) == 0
            ):  # If there are nothing but black, skip this pixel for now
                continue
            total = sum(color_ratios.values())
            weights = [ratio / total for ratio in color_ratios.values()]

            color = list(colors[np.random.choice(range(0, len(colors)), p=weights)])
            canvas.set_pixel(y0, x0, color)
            count += 1

    if count == 0:  # No need to go further.
        return canvas

    return remove_black_pixels(canvas, depth=depth + 1, max_depth=max_depth)


@dataclass()
class Group:
    """A group of pixels with the same color."""

    points: List[Tuple[int]]
    color: ArrayLike

    def __repr__(self) -> str:
        """Return a string repr of the group."""
        return f"[color: {self.color}, points: {self.points}]"

    def get_adjecent_points(self) -> Iterable[Tuple[int]]:
        """Iteraterates over the adjecent points to the group."""
        points_and_neighbours = sum(
            [list(adjecent_pixels(*point)) for point in self.points], []
        )
        for point in iter(set(points_and_neighbours).difference(set(self.points))):
            yield point


def flod_fill(color_map: ArrayLike, point: Tuple[int], color: Tuple[int]) -> Group:
    """Perform a flod fill to find the current group."""
    group = Group([point], color)
    adjecent_points_with_same_color = list(
        filter(lambda point: color_map[point], list(adjecent_pixels(*point)))
    )
    while len(adjecent_points_with_same_color) > 0:
        group.points.extend(adjecent_points_with_same_color)

        new = []
        for (y, x) in adjecent_points_with_same_color:
            for point in adjecent_pixels(y, x):
                if color_map[point] and point not in group.points and point not in new:
                    new.append(point)

        adjecent_points_with_same_color = new

    return group


# TODO: Find speed ups?
def get_groups(canvas: Canvas) -> List[Group]:
    """Find the groups (the clumps of colors)."""
    grouped = []
    groups = []
    color_maps = {
        color: (canvas.tensor == np.full((HEIGHT, WIDTH, 3), color, dtype="uint8")).all(
            axis=-1
        )
        for color in COLORS
    }
    for (y0, x0) in tqdm(canvas.pixels()):
        if (y0, x0) not in grouped:
            # Group pixels of the same colors together using flod fill
            color = tuple(canvas.get_color_of_pixel(y0, x0))

            groups.append(flod_fill(color_maps[color], (y0, x0), color))

            grouped.extend(groups[-1].points)

    return groups


def find_group(point: Tuple[int], groups: List[Group]) -> Group:
    """Find the group which the point belongs to."""
    for group in groups:
        if point in group.points:
            return group


def pick_color(colors_and_weights: Dict[Tuple[int], int]) -> Tuple[int]:
    """Pick a color randomly based on the weights."""
    total = sum(colors_and_weights.values())
    n = random.randint(0, total)
    sum_of_weights = 0
    for color, weight in colors_and_weights.items():
        if n <= sum_of_weights + weight:
            return color
        else:
            sum_of_weights += weight


def remove_blobs(canvas: Canvas) -> Canvas:
    """Remove the blobs thats inside of a bigger blob (of a different color)."""
    old_canvas = deepcopy(canvas)
    groups = get_groups(canvas)

    list_of_lengths = [len(group.points) for group in groups]
    distr = {n: list_of_lengths.count(n) for n in sorted(list(set(list_of_lengths)))}
    print(
        f"Found {len(groups)} group, with the number of pixels in each group taking the distribution: {distr}"
    )
    for idx, group in enumerate(groups):
        # TODO: MAKE THIS WEIGHTED.
        colors_and_weights = {}
        for (y, x) in group.get_adjecent_points():
            adjecent_group = find_group((y, x), groups)
            color = tuple(old_canvas.get_color_of_pixel(y, x))
            colors_and_weights[color] = colors_and_weights.get(color, 0) + len(
                adjecent_group.points
            )

        # Color the group if it's sorrounded by the same color
        if len(colors_and_weights) == 1 or len(group.points) <= 16:
            color = np.array(pick_color(colors_and_weights))
            for (y, x) in group.points:
                canvas.set_pixel(y, x, color)

    return canvas


def main():
    """Run the script."""
    canvas = random_walk(Canvas(WIDTH, HEIGHT))
    canvas.save("random_walk.png")

    print("removing black pixles.")
    canvas = remove_black_pixels(canvas)
    canvas.save("after_removing_black_pixels.png")

    print("removing blobs.")
    for _ in range(PASSES_REMOVING_NOISE):
        canvas = remove_blobs(canvas)

    canvas.save("after_removing_noise.png")

    scale_up_by(canvas, SCALE).save("scaled.png")


if __name__ == "__main__":
    main()
