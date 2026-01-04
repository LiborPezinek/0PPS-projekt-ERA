from config import BOUNDS

class Scene:
    def __init__(self,  bounds=BOUNDS):
        """
        bounds: ((xmin, xmax), (ymin, ymax), (zmin, zmax))
        """
        self.bounds = bounds
        self.stations = []
        self.targets = []

    # ---- stations ----
    def add_station(self, station):
        self._check_bounds(station.get_position())
        self.stations.append(station)

    def remove_station(self, station_id):
        self.stations = [s for s in self.stations if s.id != station_id]

    def get_stations(self):
        return self.stations

    # ---- targets ----
    def add_target(self, target):
        self._check_bounds(target.get_position())
        self.targets.append(target)

    def remove_target(self, target_id):
        self.targets = [t for t in self.targets if t.id != target_id]

    def get_targets(self):
        return self.targets

    # ---- utilities ----
    def reset(self):
        self.stations.clear()
        self.targets.clear()

    def _check_bounds(self, position):
        (xmin, xmax), (ymin, ymax), (zmin, zmax) = self.bounds
        x, y, z = position
        if not (xmin <= x <= xmax and ymin <= y <= ymax and zmin <= z <= zmax):
            raise ValueError(f"Position {position} out of bounds")

    def __repr__(self):
        return (
            f"Scene(stations={len(self.stations)}, "
            f"targets={len(self.targets)}, bounds={self.bounds})"
        )
