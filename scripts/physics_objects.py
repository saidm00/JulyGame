import math
import glm

from scripts import util

CIRCLE, SEGMENT, RECTANGLE = range(3)
STATIC, DYNAMIC = range(2)
DEFAULT, PLAYER = range(2)


def circle_collision(center, point, radius):
    if glm.distance(point, center) < radius:
        return center, glm.normalize(point - center), radius


class PhysicsObject(object):
    collision_type = STATIC
    radius = 0

    def get_top(self, pos):
        return self.get_y() + self.get_height(pos)

    def get_y(self):
        return 0

    def get_height(self, pos):
        return 0


class Circle(PhysicsObject):
    collider_type = CIRCLE
    radius = 1
    radius_sqrd = radius ** 2

    def __init__(self, x, y, z, h):
        self.pos = glm.vec3(x, y, z)
        self.height = h

    def set_radius(self, r):
        self.radius = r
        self.radius_sqrd = r ** 2

    def get_y(self):
        return self.pos.y

    def get_height(self, pos):
        return self.height


class Segment(PhysicsObject):
    collider_type = SEGMENT

    def __init__(self, start, end, y=0, height=16):
        self.y = y
        self.height = height
        self.radius = .4

        self.start = glm.vec2(*start)
        end = glm.vec2(*end)

        self.center = (self.start + end) * .5

        diff = end - self.start

        self.half_length = glm.length(diff) * .5
        self.direction = glm.normalize(diff)
        self.normal = glm.normalize(glm.vec2(-diff.y, diff.x))

    def get_y(self):
        return self.y

    def get_height(self, pos):
        return self.height


class Box(PhysicsObject):
    collider_type = RECTANGLE

    def __init__(self, pos, size, angle=0):
        self.radius = 0

        self.pos = glm.vec3(*pos)
        self.half_size = glm.vec3(*size) * .5

        rads = glm.radians(angle)
        cos = math.cos(rads)
        sin = math.sin(rads)
        self.forward = glm.vec2(cos, -sin)
        self.right = glm.vec2(sin, cos)

    def get_y(self):
        return self.pos.y

    def get_height(self, pos):
        return self.half_size.y


class DoorCollider(PhysicsObject):
    collision_type = DYNAMIC

    def __init__(self, x, y, z, rest_angle=0, length=4):
        self.pos = glm.vec3(x, y, z)
        self.end_pos = glm.vec2()
        self.direction = glm.vec2()
        self.normal = glm.vec2()
        self.angular_force = 0
        self.radius = .5

        self.angular_velocity = 0
        self.angle = rest_angle
        self.rest_angle = rest_angle

        self.length = length
        self.height = 6

        self.colliding = set()
        self.update_normal()

        self.collided = False

    def remove_colliding(self, other):
        self.colliding.remove(other)

    def collide(self, other):
        total_radius = other.radius + self.radius

        diff = other.pos.xz - self.pos.xz
        cross = glm.dot(diff, self.normal)

        if abs(cross) < total_radius:
            dot = glm.dot(diff, self.direction)

            if -total_radius < dot < self.length + total_radius:
                return cross, dot

    def collide_dynamic(self, other, collision_info):
        if other.get_y() - self.height < self.pos.y < other.get_top(self.pos.xz):
            # colliding in 3D
            cross, dot = collision_info

            force = glm.dot(other.vel.xz, self.normal)

            d = cmp(cross, 0)

            if abs(cross) < .1:
                self.angular_force += 10
            else:
                self.angular_force += (10 / cross) * abs(force)

            force = self.normal * max(0, -glm.dot(other.vel.xz, d * self.normal))

            mass = .2

            other.force.x += force.x * mass * d
            other.force.z += force.y * mass * d

            self.collided = True

            return True

        else:
            # not colliding in 3D
            self.colliding.add(other)

    def update(self, dt):
        if not self.collided:
            if self.angle != self.rest_angle:
                self.angular_force = util.angle_diff(self.angle, self.rest_angle) * .1

        if self.angular_force:
            self.angular_velocity += self.angular_force
            self.angle += self.angular_velocity * dt
            self.angular_force = 0

            self.angular_velocity *= .9

            self.update_normal()

        self.collided = False

    def update_normal(self):
        rads = glm.radians(90 - self.angle)

        cos = math.cos(rads)
        sin = math.sin(rads)

        self.end_pos.x = self.pos.x + cos * self.length
        self.end_pos.y = self.pos.z + sin * self.length

        self.direction = glm.normalize(self.end_pos - self.pos.xz)
        self.normal.x = -self.direction.y
        self.normal.y = self.direction.x


class DynamicCircle(Circle):
    collision_type = DYNAMIC
    collision_filter = DEFAULT
    bounciness = .1
    step_height = 1

    sleeping = False

    def __init__(self, x, y, z, h, parent=None):
        Circle.__init__(self, x, y, z, h)
        self.parent = parent
        self.vel = glm.vec3()
        self.force = glm.vec3()
        self.last_y = 0
        self.colliding = set()
        self.platform = None

    def spawn(self, pos, vel):
        self.pos = pos
        self.vel = vel

    def remove_colliding(self, other):
        self.colliding.remove(other)
        if other is self.platform:
            self.remove_platform()

    def remove_platform(self):
        self.platform = None
        self.on_platform_remove()

    def set_platform(self, other):
        self.platform = other
        self.on_platform(other)
        self.vel.y = 0

    def hit_top(self, other):
        self.vel.y = 0
        self.pos.y = other.get_y() - self.height
        self.on_hit_top(other)

    def on_collision(self, other, hit_point, normal_vector, radius):
        pass

    def on_platform(self, other):
        pass

    def on_platform_remove(self):
        pass

    def on_hit_top(self, other):
        pass

    def get_velocity(self):
        return glm.length(self.vel.xz)

    def collide(self, other):
        total_radius = other.radius + self.radius

        if other.collider_type == CIRCLE:
            return circle_collision(other.pos.xz, self.pos.xz, total_radius)

        elif other.collider_type == SEGMENT:
            diff = self.pos.xz - other.center
            cross = glm.dot(diff, other.normal)

            if abs(cross) < total_radius:
                dot = glm.dot(diff, other.direction)

                if abs(dot) < other.half_length:
                    return (other.center + dot * other.direction,
                            other.normal * cmp(cross, 0),
                            -1)

                elif abs(dot) < other.half_length + total_radius:
                    circle_center = other.center + other.direction * other.half_length * cmp(dot, 0)

                    return circle_collision(circle_center, self.pos.xz, total_radius)

        elif other.collider_type == RECTANGLE:
            diff = self.pos.xz - other.pos.xz
            dot = glm.dot(diff, other.forward)
            cross = glm.dot(diff, other.right)

            if abs(cross) < other.half_size.x + total_radius:
                if abs(dot) < other.half_size.z:
                    return (other.pos.xz + dot * other.forward + other.right * other.half_size.x * cmp(cross, 0),
                            other.right * cmp(cross, 0),
                            -1)

                elif abs(dot) < other.half_size.z + other.radius:
                    circle_center = other.pos.xz + \
                                    other.forward * cmp(dot, 0) * other.half_size.z + \
                                    other.right * cmp(cross, 0) * other.half_size.x
                    return circle_collision(circle_center, self.pos.xz, total_radius)

            if abs(dot) < other.half_size.z + total_radius:

                if abs(cross) < other.half_size.x:
                    return (other.pos.xz + cross * other.right + other.forward * other.half_size.z * cmp(dot, 0),
                            other.forward * cmp(dot, 0),
                            -1)

                elif abs(cross) < other.half_size.x + other.radius:
                    circle_center = other.pos.xz + \
                                    other.forward * cmp(dot, 0) * other.half_size.z + \
                                    other.right * cmp(cross, 0) * other.half_size.x
                    return circle_collision(circle_center, self.pos.xz, total_radius)

    def move_y(self, dt):
        for other in self.colliding.copy():
            if self.collide(other):
                # still colliding in 2D

                if self.vel.y < 0:
                    # falling
                    top = other.get_top(self.pos.xz)
                    if self.pos.y < top and (other.get_y() < self.pos.y or top < self.last_y):
                        # hit platform

                        self.pos.y = top
                        self.set_platform(other)

                        return True
                else:
                    # jumping

                    top = other.get_top(self.pos.xz)
                    bottom = other.get_y()

                    if self.last_y < bottom - self.height < self.pos.y:
                        # hit head

                        self.hit_top(other)
                        return True

                    elif bottom < self.pos.y < top:
                        # hit platform

                        # self.pos.y = top
                        self.set_platform(other)
                        return True

            else:
                # stopped colliding in 2D

                self.remove_colliding(other)

    def collide_dynamic(self, other, collision_info, reverse_normal=False):
        self.sleeping = False
        # started colliding in 2D
        top = other.get_top(self.pos.xz)
        step_top = top - self.step_height
        if other.get_y() - self.height < self.pos.y < step_top:
            # colliding in 3D
            hit_point, normal_vector, radius = collision_info

            if reverse_normal:
                solve_force = -1
            else:
                solve_force = 1

            force = normal_vector * max(0, -glm.dot(self.vel.xz - other.vel.xz, normal_vector * solve_force))

            self.force.x += force.x * solve_force
            self.force.z += force.y * solve_force

            self.on_collision(other, hit_point, normal_vector, radius)

            return True

        else:
            # not colliding in 3D
            self.colliding.add(other)
            if step_top < self.pos.y < top:
                # stepped on the object

                self.pos.y = top
                self.set_platform(other)

                return True

    def collide_static(self, other):
        collision_info = self.collide(other)
        if collision_info:
            # started colliding in 2D
            top = other.get_top(self.pos.xz)
            step_top = top - self.step_height
            if other.get_y() - self.get_height(None) < self.pos.y < step_top:
                # colliding in 3D
                hit_point, normal_vector, radius = collision_info

                new_pos = hit_point + normal_vector * (other.radius + self.radius + .01)
                self.pos.x, self.pos.z = new_pos
                #
                # force = glm.reflect(self.vel.xz, -normal_vector)
                force = normal_vector * max(0, -glm.dot(self.vel.xz, normal_vector))

                self.force.x += force.x * self.bounciness
                self.force.z += force.y * self.bounciness

                # self.vel.x, self.vel.z = new_vel * self.bounciness

                self.on_collision(other, hit_point, normal_vector, radius)

                return True

            else:
                # not colliding in 3D
                self.colliding.add(other)
                if step_top < self.pos.y < top:
                    # stepped on the object

                    self.pos.y = top
                    self.set_platform(other)

                    return True

    def update(self, dt):
        self.vel += self.force
        if not self.sleeping:
            if glm.length(self.vel) < .01:
                self.sleeping = True
                self.force *= 0
            else:
                self.last_y = self.pos.y
                self.pos += self.vel * dt
                self.force *= 0

                if self.platform:
                    if self.vel.y > 0:
                        self.platform = None

                    elif self.platform is True:
                        self.pos.y = 0
                        self.vel.y = 0

                    else:
                        self.pos.y = self.platform.get_top(self.pos.xz)
                        self.vel.y = 0
                        self.last_y = self.pos.y

                elif self.pos.y < 0:
                    self.pos.y = 0
                    self.set_platform(True)
