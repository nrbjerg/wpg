# wpg config file



from typing import Tuple


def hex_to_rgb(hex_repr: str) -> Tuple[int]:
    """Converts the hex representation to an tuple of rgb values."""
    r = int(hex_repr[1:3], 16)
    g = int(hex_repr[3:5], 16)
    b = int(hex_repr[5:], 16)

    return (r, g, b)

# MODIFIED VERISON OF THE DOOM ONE COLOR SCHEME (WHICH IS BASED ON ATOM ONE / ONE DARK.)
# NOTE: This has to be in RGB, use the hex_to_rgb function if needed.
COLORS_AND_RATIOS = {
    (187, 194, 207): 2,  # FG
    (152, 190, 101): 6,  # Green
    (236, 190, 123): 4,  # Yellow
    (81, 175, 239): 4,  # Blue
    (209, 147, 227): 4,  # MAGENTA
}

# GRUVBOX (DARK VERSION)
"""COLORS_AND_RATIOS = {
    (146, 131, 116): 2,  # BG
    (251, 73, 52): 4,  # RED
    (184, 187, 38): 4,  # GREEN
    (250, 189, 47): 3,  # YELLOW
    (131, 165, 152): 3,  # BLUE
    (142, 192, 124): 3,  # AQUA
    (254, 128, 25): 2,  # ORANGE
    (235, 219, 178): 2,  # FG
}"""


COLORS = list(COLORS_AND_RATIOS.keys())
RATIOS = list(COLORS_AND_RATIOS.values())

# PLEASE MAKE SURE THAT THE SCALE DIVIDES 1920 and 1080 or your perspective resolution.
SCALE = 4
WIDTH = 1920  # SCALE
HEIGHT = 1080 # SCALE
CUTOF = 16  # If the group is larger than this it's not automatically given a new color.
PASSES_REMOVING_NOISE = 2  # If you dont care about noise, set this to 0, the image generation will be much faster then.
PROBABILITY_FOR_COLOR_TO_STAY_THE_SAME = 0.9998
# NOTE: the * 100 makes sure that there aren't many black pixels after the random walk process.
NUMBER_OF_STEPS = WIDTH * HEIGHT * 100
