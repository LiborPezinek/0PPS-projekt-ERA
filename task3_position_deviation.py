import numpy as np
import matplotlib.pyplot as plt

from engine import estimate_position, simulate_time_of_arival, compute_time_difference_of_arival
from visualization import plot_scenario, plot_hyperbolas, compute_bounds

# Equilateral triangle with reference station at center
####################
radius = 4000.0
center_x, center_y = 0.0, 0.0
stationOffsetY = 200.0   # intentional error in one station's position

stationsActual = np.array([
    [center_x, center_y, 0.0],   # S0 – referenční stanice (center)
    [center_x + radius * np.cos(np.radians(90)), center_y + radius * np.sin(np.radians(90)), 0.0],   # S1 at 90°
    [center_x + radius * np.cos(np.radians(210)), center_y + radius * np.sin(np.radians(210)) + stationOffsetY, 0.0],   # S2 at 210°
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

# toa = simulate_time_of_arival(stationsActual, target, sigma=1e-9)   # toa is measured in reality
# tdoa = compute_time_difference_of_arival(toa)

# estimate = estimate_position(stationsFake, tdoa, x0)

# xmin, xmax, ymin, ymax = compute_bounds(
#         stationsFake, target, estimate
#     )
# plot_scenario(stationsFake, target, estimate)
# plot_hyperbolas(stationsFake, tdoa, z_plane=estimate[2], xlim=(xmin, xmax), ylim=(ymin, ymax))
# plt.show(block=True)

###############################################

# Experiment: Vliv chyby v poloze jednotlivých přijímacích stanic na chybu odhadu polohy vysílače
stationErrors = np.linspace(0, 500, 50)  # from 0 to 500 meters

estimateErrors = [[[],[],[]], [[],[],[]], [[],[],[]]]  # for each station and axis
for error in stationErrors:
    stationsTest = stationsFake.copy()
    for j in range(0, 3):  # axes x,y,z
        for i in range(1, stationsTest.shape[0]):  # stations S1, S2, S3
            stationsTest[i, j] += error  # introduce error in specified coordinate axis

            tdoaTest = compute_time_difference_of_arival(simulate_time_of_arival(stationsTest, target, sigma=1e-9))

            estimate = estimate_position(stationsFake, tdoaTest, x0)
            estimateError = np.linalg.norm(np.abs(estimate - target))
            estimateErrors[i-1][j].append(estimateError)
    

# Create plots for each station's position error impact
fig, axes = plt.subplots(3, 3, figsize=(15, 4))
    
for i in range(axes.shape[0]):
    for j in range(axes.shape[1]):
        ax = axes[i, j]
        ax.set_title(f"Station {i+1}'s {['X', 'Y', 'Z'][j]}-axis Position Error Impact On Target Estimate Error")
        ax.set_xlabel("Station Position Error (m)")
        ax.set_ylabel("Estimate Error (m)")
        ax.grid(True)
        ax.plot(stationErrors, estimateErrors[i][j], label=f'Station {i+1} Error', color='C'+str(i))


plt.tight_layout()
plt.show(block=True)
