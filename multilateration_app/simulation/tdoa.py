import numpy as np

from config import C, TIME_NOISE_STD


def simulate_arrival_times(target, stations):
    tx, ty, tz = target.get_position()
    arrival_times = {}

    for s in stations:
        sx, sy, sz = s.get_position()
        distance = np.sqrt((tx - sx)**2 + (ty - sy)**2 + (tz - sz)**2)
        time = distance / C
        noise = np.random.normal(0.0, TIME_NOISE_STD)
        arrival_times[s.id] = time + noise

    return arrival_times


def compute_tdoa(arrival_times, reference_id):
    t_ref = arrival_times[reference_id]
    tdoa = {}

    for sid, t in arrival_times.items():
        if sid == reference_id:
            continue
        tdoa[sid] = t - t_ref

    return tdoa

# ----------------------------
# Hyperbola helpers 
# ----------------------------

def range_diff_level(tdoa_value, c=C):
    return c * tdoa_value

def range_diff_field(A0, A1, plane, fixed_value, station_i_pos, station_ref_pos):

    plane = plane.lower()
    mapping = {
        "xy": (A0, A1, fixed_value),
        "xz": (A0, fixed_value, A1),
        "yz": (fixed_value, A0, A1),
    }
    try:
        X, Y, Z = mapping[plane]
    except KeyError as e:
        raise ValueError(f"Unknown plane '{plane}'. Use 'xy', 'xz', or 'yz'.") from e

    xi, yi, zi = station_i_pos
    xr, yr, zr = station_ref_pos

    Di = np.sqrt((X - xi) ** 2 + (Y - yi) ** 2 + (Z - zi) ** 2)
    Dr = np.sqrt((X - xr) ** 2 + (Y - yr) ** 2 + (Z - zr) ** 2)
    return Di - Dr
