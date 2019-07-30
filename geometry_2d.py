import math

def distance(point1, point2):
    if isinstance(point1, Vector):
        point1 = point1.x, point1.y
    if isinstance(point2, Vector):
        point2 = point2.x, point2.y
    dx = (point1[0] - point2[0]) ** 2
    dy = (point1[1] - point2[1]) ** 2
    return (dx + dy) ** 0.5

def dot(vector1, vector2):
    x = vector1.x * vector2.x
    y = vector1.y * vector2.y
    return x + y

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length = distance((0, 0), self)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector(x, y)

    def __mul__(self, scalar):
        x = self.x * scalar
        y = self.y * scalar
        return Vector(x, y)

    def __truediv__(self, scalar):
        x = self.x / scalar
        y = self.y / scalar
        return Vector(x, y)
    
    def __pow__(self, exponent):
        x = self.x ** exponent
        y = self.y ** exponent
        return Vector(x, y)

    def __neg__(self):
        x = -self.x
        y = -self.y
        return Vector(x, y)

    def __abs__(self):
        x = abs(self.x)
        y = abs(self.y)
        return Vector(x, y)
    
    def copysign(self, sign):
        x = math.copysign(self.x, sign.x)
        y = math.copysign(self.y, sign.y)
        return Vector(x, y)

    def projection(self, vector):
        vector_dot = dot(vector, vector)
        if vector_dot > 0:
            return vector * (dot(self, vector) / vector_dot)
        else:
            return self * 0

    def rotate(self, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        return Vector(x, y)