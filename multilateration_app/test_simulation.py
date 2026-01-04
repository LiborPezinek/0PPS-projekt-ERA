from simulation import Station, Target, Scene, simulate_arrival_times, compute_tdoa, estimate_position
from config import BOUNDS
import numpy as np

# --- create scene ---
scene = Scene()

# add 4 stations
scene.add_station(Station(0, (0, 0, 20)))
scene.add_station(Station(1, (1000, 0, 0)))
scene.add_station(Station(2, (0, 1000, 100)))
scene.add_station(Station(3, (1000, 1000, 0)))

# add target
target = Target(0, (600, 400, 200))
scene.add_target(target)

# --- Monte Carlo runs ---
num_runs = 10
errors = []

for i in range(num_runs):
    # simulate TDOA with noise
    arrival_times = simulate_arrival_times(target, scene.get_stations())
    tdoa = compute_tdoa(arrival_times, reference_id=0)
    
    # estimate position
    estimated_pos = estimate_position(
        scene.get_stations(),
        reference_id=0,
        tdoa=tdoa,
        initial_guess=(500, 500, 100)
    )
    
    # compute error vector
    error = tuple(a - b for a, b in zip(estimated_pos, target.get_position()))
    errors.append(error)
    
    # print run results
    print(f"Run {i+1}: Estimated={estimated_pos}, Error={error}")

# --- overall statistics ---
errors = np.array(errors)
mean_error = np.mean(errors, axis=0)
std_error = np.std(errors, axis=0)

print(f"\nMean error over {num_runs} runs: {mean_error}")
print(f"Std deviation over {num_runs} runs: {std_error}")
