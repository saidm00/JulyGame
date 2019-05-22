import random
import glm


from scripts import (player,
                     loaded_terrain,
                     terrain,
                     platform,
                     wall,
                     staircase,
                     test_enemy,
                     helicopter,
                     powerup,
                     door)


class GameManager:
    def __init__(self, engine):
        self.engine = engine

        self.game_objects = []
        self.vehicles = []
        self.powerups = []

        # self.terrain = terrain.Terrain(self.engine, 128, 128, 5, 200, 0)
        self.terrain = loaded_terrain.Terrain(self.engine)
        self.engine.renderer.scene.append(self.terrain)

        self.player = player.Player(self.engine)
        self.engine.renderer.scene.append(self.player.graphics)

        for i in range(5):
            e = test_enemy.Enemy(self.engine)
            self.engine.renderer.scene.append(e)
            self.game_objects.append(e)

    def load(self):
        for y in range(100):
            x = random.randint(0, 1) * 3 - 10 + random.random() * 2
            z = random.randint(0, 1) * 3 + random.random() * 2
            platform.Hedge(self.engine, (x, y*5, z))

        for i in range(10):
            wall.Wall(self.engine, (-10 + random.random(), i * 16, -10 + random.random()))
            wall.Wall(self.engine, (10 + random.random(), i * 16, -10 + random.random() * 3))

        staircase.StairCase(self.engine, (0, 0, -6), 90)

        door.Door(self.engine, (-1.9, 4, -10), 90).spawn()

        self.test_heli = helicopter.Helicopter(self.engine, 0)
        self.test_heli.spawn(glm.vec3(0, 25, 10))

        powerup.Health(self.engine, 0, (0, 3, 20)).spawn()
        powerup.Fuel(self.engine, 0, (0, 3, 16)).spawn()

    def remove_object(self, obj):
        obj.despawn()
        self.game_objects.remove(obj)

    def update(self, dt):
        self.player.update(dt)

        for o in tuple(self.game_objects):
            o.update(dt)

        for p in tuple(self.powerups):
            p.update(dt)
