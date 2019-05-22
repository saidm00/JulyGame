import code


class Physics:
    def __init__(self, engine):
        self.engine = engine

        self.static = []
        self.dynamic = []
        self.bullets = []
        self.doors = []

        # code.interact(local=locals())

    def update(self, dt):
        for obj in self.dynamic:
            obj.move_y(dt)
            obj.update(dt)

        # player_batch = self.get_batch(self.engine.game_manager.player.collider.pos)
        # print len(batches[player_batch])

        for d in self.doors:
            d.update(dt)
            for obj in self.dynamic:
                if not obj.sleeping:
                    collision_info = d.collide(obj)
                    if collision_info:
                        d.collide_dynamic(obj, collision_info)

            for b in self.bullets:
                collision_info = d.collide(b)
                if collision_info:
                    d.collide_dynamic(b, collision_info)
                    b.on_collision(d)

        for b in tuple(self.bullets):
            b.update(dt)
            for obj in self.dynamic:
                if obj.collision_filter == b.collision_filter:
                    collision_info = b.collide(obj)
                    if collision_info:
                        obj.collide_dynamic(b, collision_info, True)
            else:
                for obj in self.static:
                    if b.collide_static(obj):
                        break

        for i, obj in enumerate(self.dynamic):
            for dynamic_obj in self.dynamic[i+1:]:
                if not (obj.sleeping and dynamic_obj.sleeping):
                    if dynamic_obj not in obj.colliding:
                        collision_info = obj.collide(dynamic_obj)
                        if collision_info:
                            obj.collide_dynamic(dynamic_obj, collision_info)
                            dynamic_obj.collide_dynamic(obj, collision_info, True)

            if not obj.sleeping:
                for static_obj in self.static:
                    obj.collide_static(static_obj)
