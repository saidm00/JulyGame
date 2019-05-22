# todo: comment

import math

from scripts import (physics,
                     door)


def segment(start, end, y, h, r):
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    length = (dx ** 2 + dy ** 2) ** .5

    nx = (dx * r) / length
    ny = (dy * r) / length

    vertices = [start[0] + nx, start[1] + ny,
                end[0] - nx, end[1] - ny]

    return y, h, vertices, r


def rectangle(w, l, y, h):
    vertices = []
    for i in (-w, w):
        for j in (-l, l):
            vertices.append(i)
            vertices.append(j)
    # vertices = [(x, y) for x in (-w, w) for y in (-l, l)]
    return y, h, vertices


def circle(pos, y, h, r):
    return y, h, pos, r


class Building:
    r = .3
    base_size = 8.1
    j = 8 - r
    data = [['models/environment/test_building', 'wood.png',
             [segment((8, 8), (8, -8), 7.6, 8.8, r),
              segment((8, -1.9), (8, -8), .5, 15.9, r),
              segment((8, 1.9), (8, 8), .5, 15.9, r),
              segment((-8, -8), (8, -8), .5, 15.9, r),
              segment((-8, 8), (8, 8), .5, 15.9, r),
              segment((-8, -8), (-8, 8), .5, 15.9, r),
              rectangle(8.1 + r, 8.1 + r, 0, .5),
              rectangle(8.1 + r, 8.1 + r, 16, .5),
              ],
             [[7.5, 0.5, 0.0]]],

            ['models/environment/wall', 'wood.png',
             [segment((-8, 0), (8, 0), 0, 16, r)],
             []],

            ['models/environment/sky_scraper', 'highrise.png',
             [segment((-15, -15), (15, -15), 0, 200, 1),
              segment((15, -15), (15, 15), 0, 200, 1),
              segment((15, 15), (-15, 15), 0, 200, 1),
              segment((-15, 15), (-15, -15), 0, 200, 1),
              rectangle(15, 15, 0, 197)],
             []],

            ['models/environment/bridge', 'metal.png',
             [rectangle(16, 5, -2.5, 2.5),
              rectangle(35.474 / 2, 5, 8, 2),
              circle((15, -4), 0, 8, .4),
              circle((0, -4), 0, 8, .4),
              circle((-15, -4), 0, 8, .4),
              circle((15, 4), 0, 8, .4),
              circle((0, 4), 0, 8, .4),
              circle((-15, 4), 0, 8, .4),
              ],
             []],

            ['models/environment/streetlamp', 'metal.png',
             [segment((22, 0), (22-8.25, 0), 15.2, 2, .8),
              circle((22, 0), 0, 15.2, .4),

              segment((-22, 0), (-(22 - 8.25), 0), 15.2, 2, .8),
              circle((-22, 0), 0, 15.2, .4),
              ],
             []],

            ['models/environment/canopy', 'metal.png',
             [rectangle(15, 15, 15, 2.2),
              circle((-13, -13), 0, 15, 1),
              circle((13, -13), 0, 15, 1),
              circle((-13, 13), 0, 15, 1),
              circle((13, 13), 0, 15, 1),
              ],
             []],

            ['models/environment/air_vent', 'metal.png',
             [circle((0, 0), 0, 2.2, 2.4),
              ],
             []],

            ['models/environment/barrier', 'metal.png',
             [rectangle(6, 1, 0, 4),
              ],
             []],

            ]

    def __init__(self, app, data, pos=(0, 0, 0), angle=0):
        self.app = app

        mesh_name, texture, colliders, doors = data

        rads = angle / 57.3
        cos = math.cos(rads)
        sin = math.sin(rads)

        transform = pymunk.Transform(a=cos, b=-sin,
                                     c=sin, d=cos,
                                     tx=pos[0], ty=pos[2])

        f = pymunk.ShapeFilter(categories=physics.STATIC_FILTER)

        self.colliders = []
        for c in colliders:
            vertices = zip(c[2][::2], c[2][1::2])

            if len(c) == 3:
                collider = pymunk.Poly(self.app.physics.space.static_body,
                                       vertices=vertices,
                                       transform=transform)

            elif len(c) == 4:
                if len(vertices) == 1:
                    x1 = vertices[0][0] * transform.a + vertices[0][1] * transform.c + transform.tx
                    y1 = vertices[0][0] * transform.b + vertices[0][1] * transform.d + transform.ty
                    collider = pymunk.Circle(self.app.physics.space.static_body, c[3],
                                             (x1, y1))
                else:
                    x1 = vertices[0][0] * transform.a + vertices[0][1] * transform.c + transform.tx
                    y1 = vertices[0][0] * transform.b + vertices[0][1] * transform.d + transform.ty
                    x2 = vertices[1][0] * transform.a + vertices[1][1] * transform.c + transform.tx
                    y2 = vertices[1][0] * transform.b + vertices[1][1] * transform.d + transform.ty
                    collider = pymunk.Segment(self.app.physics.space.static_body,
                                              (x1, y1), (x2, y2), c[3])

            collider.y = pos[1] + c[0]
            collider.height = c[1]
            collider.collision_type = physics.STATIC
            collider.filter = f
            self.colliders.append(collider)

        self.doors = []
        for x, y, z in doors:
            door_x = pos[0] + (cos * x + sin * z)
            door_y = pos[1] + y
            door_z = pos[2] + (-sin * x + cos * z)
            d = door.Door(self.app,
                          pos=(door_x, door_y, door_z),
                          angle=angle)
            self.doors.append(d)

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            Color(1, 1, 1)
            self.pos = Translate(*pos)
            Rotate(angle, 0, 1, 0)

            self.app.graphic_data.draw_instance(mesh_name,
                                                self.canvas,
                                                texture=texture)

            PopMatrix()

    def spawn(self):
        for d in self.doors:
            d.spawn()
        self.app.physics.space.add(*self.colliders)
        self.app.renderer.scene.add(self.canvas)
        self.app.game_manager.game_objects.add(self)

    def update(self, dt):
        pass

    def despawn(self):
        self.app.physics.remove(self.colliders)
        self.app.renderer.scene.remove(self.canvas)
