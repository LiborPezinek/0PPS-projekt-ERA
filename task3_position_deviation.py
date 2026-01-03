import numpy as np
import matplotlib.pyplot as plt

from engine import estimate_position, simulate_time_of_arival, compute_time_difference_of_arival
from visualization import plot_scenario, plot_hyperbolas, compute_bounds

# Equilateral triangle with reference station at center
####################
radius = 4000.0
center_x, center_y = 0.0, 0.0

stationsActual = np.array([
    [center_x, center_y, 0.0],   # S0 – referenční stanice (center)
    [center_x + radius * np.cos(np.radians(90)), center_y + radius * np.sin(np.radians(90)), 0.0],   # S1 at 90°
    [center_x + radius * np.cos(np.radians(210)), center_y + radius * np.sin(np.radians(210)) + 200.0, 0.0],   # S2 at 210°
    [center_x + radius * np.cos(np.radians(330)), center_y + radius * np.sin(np.radians(330)), 0.0],   # S3 at 330°
])

stationsFake = np.array([
    [center_x, center_y, 0.0],   # S0 – referenční stanice (center)
    [center_x + radius * np.cos(np.radians(90)), center_y + radius * np.sin(np.radians(90)), 0.0],   # S1 at 90°
    [center_x + radius * np.cos(np.radians(210)), center_y + radius * np.sin(np.radians(210)), 0.0],   # S2 at 210°
    [center_x + radius * np.cos(np.radians(330)), center_y + radius * np.sin(np.radians(330)), 0.0],   # S3 at 330°
])
####################

target = np.array([
    2200.0, 5500.0, 1000.0
])

x0 = np.array([0, 0, 0])

###############################################

toa = simulate_time_of_arival(stationsActual, target, sigma=1e-9)   # toa is measured in reality
tdoa = compute_time_difference_of_arival(toa)

estimate = estimate_position(stationsFake, tdoa, x0)

xmin, xmax, ymin, ymax = compute_bounds(
        stationsFake, target, estimate
    )
plot_scenario(stationsFake, target, estimate)
plot_hyperbolas(stationsFake, tdoa, z_plane=estimate[2], xlim=(xmin, xmax), ylim=(ymin, ymax))
plt.show(block=True)

###############################################
# Nepřesně určená poloha přijímací stanice má výrazný vliv na odhadovanou polohu vysílače.
# I při velmi malém šumu v měření TDOA (sigma=1e-9) vede chyba 200 m v poloze jedné ze stanic k chybě přes 1000 m v odhadu polohy vysílače.

# TODO: Vykreslit závislost chyby na nepřesnosti polohy stanice.
###############################################