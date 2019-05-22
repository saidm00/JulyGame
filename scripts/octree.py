import glm


class Tree:

    def __init__(self, n, center=glm.vec3(.5), size=.5):
        self.n = n
        self.center = center
        self.size = size
        self.tree = {}

        self.directions = {}
        for z in (0, 1):
            for y in (0, 1):
                for x in (0, 1):
                    self.directions[x + y * 2 + z * 4] = glm.vec3(cmp(x, .5),
                                                                  cmp(y, .5),
                                                                  cmp(z, .5))

    def display(self):
        self.draw_tree(self.tree)

    def draw_tree(self, tree, tabs=0):
        for k, v in tree.iteritems():
            print '{}{}'.format(' ' * tabs, k)
            if isinstance(v, dict):
                self.draw_tree(v, tabs + 1)
            else:
                for i in v:
                    print '{}{}'.format(' ' * (tabs + 1), i)

    def get_octants(self, obj, center):
        octants = []
        diffs = [[(cmp(i, 0) + 1) / 2] if cmp(i, 0) else [0, 1] for i in obj.pos - center]
        for x in diffs[0]:
            for y in diffs[1]:
                for z in diffs[2]:
                    octants.append(x + y * 2 + z * 4)
        return octants

    def populate(self, objs):
        self.tree = self.create_tree(objs, self.center, self.size)

    def create_tree(self, objs, center, size):
        tree = {}
        for o in objs:
            for d in self.get_octants(o, center):
                if d in tree:
                    tree[d].append(o)
                else:
                    tree[d] = [o]

        new_size = size * .5
        for k, v in tree.iteritems():
            if len(v) > self.n:
                tree[k] = self.create_tree(v, center + new_size * self.directions[k], new_size)
            else:
                tree[k] = v

        return tree

    def collide(self, obj):
        return self.find_collisions(obj, self.tree, self.center, self.size)

    def find_collisions(self, obj, tree, center, size):
        directions = self.get_octants(obj, center)

        collisions = []
        for direction in directions:
            if direction in tree:
                move_data = tree[direction]
                if isinstance(move_data, dict):
                    new_size = size * .5
                    collisions.extend(self.find_collisions(obj, move_data,
                                                           center + new_size * direction,
                                                           new_size))
                else:
                    collisions.extend(move_data)
        return collisions
