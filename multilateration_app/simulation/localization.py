import numpy as np
from scipy.optimize import least_squares

from config import C


def residuals_func(pos, stations, reference_id, tdoa):
    x, y, z = pos
    res = []
    s_ref = next(s for s in stations if s.id == reference_id)
    xr, yr, zr = s_ref.get_position()

    for s in stations:
        if s.id == reference_id:
            continue
        xs, ys, zs = s.get_position()
        di = np.sqrt((x - xs)**2 + (y - ys)**2 + (z - zs)**2)
        dr = np.sqrt((x - xr)**2 + (y - yr)**2 + (z - zr)**2)
        delta_d = di - dr
        res.append(delta_d - C * tdoa[s.id])

    return np.array(res)


def estimate_position(stations, reference_id, tdoa, initial_guess=(0, 0, 0)):
    result = least_squares(
        residuals_func,
        x0=np.array(initial_guess),
        args=(stations, reference_id, tdoa),
    )
    return result.x
