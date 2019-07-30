import math
import pygame as pg
from geometry_2d import Vector, distance

class Puck:

    def __init__(self, pos=(200, 200), size=10):
        self.pos = Vector(pos[0], pos[1])
        self.pos_future = self.pos
        self.pos_tuple = pos
        self.size = size
        self.mass = 2 * math.pi * size
        self.vel = Vector(0, 0)
        self.forces = Vector(0, 0)
        self.being_dragged = False

    def collide(self, other_pos, other_size, other_mass, other_vel):
        normal = other_pos - self.pos
        tangent = Vector(-normal.y, normal.x)
        total_size = self.size + other_size
        total_mass = self.mass + other_mass
        puck_normal = Vector.projection(self.vel, normal)
        puck_tangent = Vector.projection(self.vel, tangent)
        other_normal = Vector.projection(other_vel, normal)
        relative_normal = other_normal - puck_normal
        relative_normal_vel = relative_normal.length
        overlap = total_size - normal.length
        if relative_normal_vel > 0.00001:
            overlap_time = overlap / relative_normal_vel
            self.pos -= puck_normal * overlap_time
            puck_normal = (relative_normal * other_mass + puck_normal * self.mass + other_normal * other_mass) / total_mass
            self.pos += puck_normal * overlap_time
        self.vel = (puck_normal + puck_tangent) * 0.6

    def drag(self, mouse_pos):
        self.forces += (Vector(mouse_pos[0], mouse_pos[1]) - self.pos) * 1000

    def update(self, timestep):
        self.vel *= 0.999
        acceleration = self.forces / self.mass
        end_vel = self.vel + acceleration * timestep
        self.vel = (self.vel + end_vel) / 2
        self.pos += self.vel * timestep
        self.pos_tuple = self.pos.x, self.pos.y
        self.vel = end_vel
        self.forces = Vector(0, 0)

        hit_left_wall = self.pos.x - self.size < 0
        hit_right_wall = self.pos.x + self.size > 400
        hit_top_wall = self.pos.y - self.size < 0
        hit_bottom_wall = self.pos.y + self.size > 400

        if hit_left_wall or hit_right_wall:
            self.vel.x *= -0.6
            if hit_left_wall:
                self.pos.x += -(self.pos.x - self.size) * 2
            if hit_right_wall:
                self.pos.x += (400 - (self.pos.x + self.size)) * 2
        if hit_top_wall or hit_bottom_wall:
            self.vel.y *= -0.6
            if hit_top_wall:
                self.pos.y += -(self.pos.y - self.size) * 2
            if hit_bottom_wall:
                self.pos.y += (400 - (self.pos.y + self.size)) * 2

class Spring:
    def __init__(self, puck1, puck2, stiffness=1, length=None):
        self.puck1 = puck1
        self.puck2 = puck2
        self.stiffness = stiffness
        self.strength = stiffness * 1000
        self.length = length
        if length is None:
            self.length = distance(puck1.pos, puck2.pos)

    def update(self):
        offset = distance(self.puck1.pos, self.puck2.pos) - self.length
        relative_vel = self.puck1.vel - self.puck2.vel
        if abs(offset) >= 0.001 or relative_vel.length >= 0.0001:
            d = (self.puck2.pos - self.puck1.pos)
            angle = math.atan2(d.y, d.x)
            while angle < 0:
                angle += 2 * math.pi
            while angle >= 2 * math.pi: 
                angle -= 2 * math.pi
            force = (Vector(abs(d.x), abs(d.y)) - Vector(abs(math.cos(angle) * self.length), abs(math.sin(angle) * self.length))) * self.strength
            if d.x < 0:
                force.x *= -1
            if d.y < 0:
                force.y *= -1
            self.puck1.forces += (abs(force) - self.puck1.vel).copysign(force)
            self.puck2.forces -= (abs(force) - self.puck2.vel).copysign(force)

pg.init()

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

RES = 400, 400

WINDOW = pg.display.set_mode(RES)
CLOCK = pg.time.Clock()

GRAVITY = Vector(0, 200)

PUCKS = []
SPRINGS = []

TIME = 0

MOUSE_HELD = False
PAUSED = False

RUNNING = True
while RUNNING:

    DT = CLOCK.tick(120) * 1e-3

    WINDOW.fill(BLACK)

    MOUSE_POS = pg.mouse.get_pos()

    for spring in SPRINGS:
        pg.draw.line(WINDOW, WHITE, spring.puck1.pos_tuple, spring.puck2.pos_tuple, 3)
        if not PAUSED:
            spring.update()

    for i, puck in enumerate(PUCKS):
        pg.draw.circle(WINDOW, RED, (int(puck.pos.x), int(puck.pos.y)), puck.size)
        for other in PUCKS[i+1:]:
            if distance(other.pos, puck.pos) < puck.size + other.size:
                vel = puck.vel
                puck.collide(other.pos, other.size, other.mass, other.vel)
                other.collide(puck.pos, puck.size, puck.mass, vel)
        if MOUSE_HELD:
            if puck.being_dragged:
                puck.drag(MOUSE_POS)
                pg.draw.line(WINDOW, WHITE, MOUSE_POS, puck.pos_tuple)
        if not PAUSED:
            #puck.forces += GRAVITY * puck.mass
            puck.update(DT)

    pg.display.update()

    TIME += DT

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            RUNNING = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                MOUSE_HELD = True
                for puck in PUCKS:
                    if distance(MOUSE_POS, puck.pos) <= puck.size:
                        puck.being_dragged = True
            elif event.button == 2:
                if len(PUCKS) < 100:
                    PUCKS.append(Puck(MOUSE_POS))
            elif event.button == 3:
                for puck in PUCKS:
                    if distance(MOUSE_POS, puck.pos) <= puck.size:
                        PUCKS.remove(puck)
                        removed = []
                        for spring in SPRINGS:
                            if puck in [spring.puck1, spring.puck2]:
                                removed.append(spring)
                        for spring in removed:
                            SPRINGS.remove(spring)
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                MOUSE_HELD = False
                for puck in PUCKS:
                    if puck.being_dragged:
                        for other in PUCKS:
                            if distance(MOUSE_POS, other.pos) <= other.size and puck != other:
                                SPRINGS.append(Spring(puck, other, 10))
                        puck.being_dragged = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                PAUSED = not PAUSED
                for puck in PUCKS:
                    puck.forces = Vector(0, 0)
                    puck.vel = Vector(0, 0)