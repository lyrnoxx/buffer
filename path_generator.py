
# path_generator.py
import numpy as np

def generate_lawnmower(area_bounds, swath_width, height, step=5):
    """
    area_bounds = (xmin, xmax, ymin, ymax)
    swath_width = width covered per pass
    height = fixed altitude
    Returns: list of waypoints [(x, y, z), ...]
    """
    xmin, xmax, ymin, ymax = area_bounds
    z = -abs(height)
    paths = []

    y_vals = np.arange(ymin, ymax, swath_width)
    direction = 1

    for y in y_vals:
        if direction == 1:
            x_path = np.linspace(xmin, xmax, int((xmax - xmin) // step))
        else:
            x_path = np.linspace(xmax, xmin, int((xmax - xmin) // step))
        direction *= -1
        for x in x_path:
            paths.append((x, y, z))
    return paths
