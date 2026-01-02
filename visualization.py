import numpy as np
import matplotlib.pyplot as plt

def compute_bounds(stations_positions, target=None, estimate=None, margin=0.2):
    """
    Computes plot bounds based on data with margin.
    margin = relative padding (20 % default)
    """
    points_2d = [stations_positions[:, :2]]

    if target is not None:
        points_2d.append(target[:2][None, :])

    if estimate is not None:
        points_2d.append(estimate[:2][None, :])

    P = np.vstack(points_2d)

    xmin, ymin = P.min(axis=0)
    xmax, ymax = P.max(axis=0)

    dx = xmax - xmin
    dy = ymax - ymin

    padding_x = dx * margin if dx > 0 else 1.0
    padding_y = dy * margin if dy > 0 else 1.0

    return (
        xmin - padding_x,
        xmax + padding_x,
        ymin - padding_y,
        ymax + padding_y
    )


def compute_hyperbola_xy(
    s0, si, d, z_plane,
    xlim, ylim, resolution=400
):
    """
    s0, si : (3,) stations
    d      : distance difference = c * TDOA
    z_plane: fixed z
    """
    x = np.linspace(*xlim, resolution)
    y = np.linspace(*ylim, resolution)
    X, Y = np.meshgrid(x, y)

    P = np.stack([X, Y,
                  np.full_like(X, z_plane)], axis=-1)

    r0 = np.linalg.norm(P - s0, axis=-1)
    ri = np.linalg.norm(P - si, axis=-1)

    return X, Y, ri - r0 - d

def plot_hyperbolas(
    stations,
    tdoa,
    z_plane=0.0,
    c=299_792_458.0,
    xlim=(-5000, 5000),
    ylim=(-5000, 5000)
):
    """
    Draws hyperbolas corresponding to TDOA
    """
    s0 = stations[0]

    for i in range(1, stations.shape[0]):
        d = c * tdoa[i-1]
        X, Y, F = compute_hyperbola_xy(
            s0, stations[i], d,
            z_plane, xlim, ylim
        )
        plt.contour(X, Y, F, levels=[0],
                    linestyles='--', linewidths=1)


def plot_scenario(stations, target=None, estimate=None):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 7))

    ax.scatter(stations[:, 0], stations[:, 1],
               marker='^', s=120, label='Stations')

    for i, s in enumerate(stations):
        ax.text(s[0], s[1], f"S{i}\nz={s[2]:.0f}",
                fontsize=9, ha='left', va='bottom')

    if target is not None:
        ax.scatter(target[0], target[1],
                   c='red', s=80, label='Target')
        ax.text(target[0], target[1],
                f"Target\nz={target[2]:.0f}",
                fontsize=9, ha='right')

    if estimate is not None:
        ax.scatter(estimate[0], estimate[1],
                   c='green', marker='x', s=80,
                   label='Estimate')

    xmin, xmax, ymin, ymax = compute_bounds(
        stations, target, estimate
    )

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_aspect('equal', adjustable='box')  # ← KLÍČOVÝ ŘÁDEK
    ax.grid(True)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.legend()

