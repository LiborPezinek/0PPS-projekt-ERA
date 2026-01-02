import numpy as np
import matplotlib.pyplot as plt

from engine import estimate_position, simulate_time_of_arival, compute_time_difference_of_arival
from visualization import plot_scenario, plot_hyperbolas, compute_bounds

stations = np.array([
    [0.0,    0.0,    0.0],   # S0 – referenční stanice
    [4000.0, 0.0,    0.0],   # S1
    [0.0,    4000.0, 0.0],   # S2
    [4000.0, 4000.0, 0.0],   # S3
])

target = np.array([
    2200.0, 5500.0, 1000.0
])

x0 = np.array([0, 0, target[2]])

toa = simulate_time_of_arival(stations, target, sigma=1e-9)
tdoa = compute_time_difference_of_arival(toa)

estimate = estimate_position(stations, tdoa, x0)

xmin, xmax, ymin, ymax = compute_bounds(
        stations, target, estimate
    )
plot_scenario(stations, target, estimate)
plot_hyperbolas(stations, tdoa, z_plane=target[2], xlim=(xmin, xmax), ylim=(ymin, ymax))
plt.show(block=True)
