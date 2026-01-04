
class Target:
    def __init__(self, target_id, position):
        self.id = target_id
        self.set_position(position)

    def set_position(self, position):
        if len(position) != 3:
            raise ValueError("Position must be (x, y, z)")
        self.x, self.y, self.z = position

    def get_position(self):
        return (self.x, self.y, self.z)

    def __repr__(self):
        return f"Target(id={self.id}, pos=({self.x}, {self.y}, {self.z}))"
