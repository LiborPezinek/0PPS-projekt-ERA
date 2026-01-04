
class Station:
    def __init__(self, station_id, position):
        self.id = station_id
        self.set_position(position)

    def set_position(self, position):
        if len(position) != 3:
            raise ValueError("Position must be (x, y, z)")
        self.x, self.y, self.z = position

    def get_position(self):
        return (self.x, self.y, self.z)

    def __repr__(self):
        return f"Station(id={self.id}, pos=({self.x}, {self.y}, {self.z}))"
