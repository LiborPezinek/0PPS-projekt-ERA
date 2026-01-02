import numpy as np
from scipy.optimize import least_squares

def simulate_time_of_arival(stations, target, sigma, wave_speed=299_792_458.0):
    distance = np.linalg.norm(stations - target, axis=1)
    noise = np.random.normal(0, sigma, size=distance.shape)
    return distance / wave_speed + noise


def compute_time_difference_of_arival(toa, reference_station=0):
    return np.delete(toa - toa[reference_station], reference_station)

def residual(x, stations_positions, tdoa, wave_speed):
    distance_to_ref_station = np.linalg.norm(x - stations_positions[0])
    residuals = []
    for i_station in range(1, stations_positions.shape[0]):
        distance_to_i_station = np.linalg.norm(x - stations_positions[i_station])
        residuals.append((distance_to_i_station - distance_to_ref_station) - wave_speed * tdoa[i_station-1])
    return np.array(residuals)


def estimate_position(stations, tdoa, initial_guess, wave_speed=299_792_458.0):
    solution = least_squares(
        residual,
        initial_guess,
        args=(stations, tdoa, wave_speed)
    )
    return solution.x
