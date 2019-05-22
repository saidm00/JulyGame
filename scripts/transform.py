import glm


class Transform(object):
    def __init__(self, translation, rotation, scale=glm.vec3(1.0)):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def getModel(self):
        model = glm.translate(glm.mat4(), self.translation)
        model = glm.rotate(model, self.rotation.x, glm.vec3(1.0, 0.0, 0.0))
        model = glm.rotate(model, self.rotation.y, glm.vec3(0.0, 1.0, 0.0))
        return glm.rotate(model, self.rotation.z, glm.vec3(0.0, 0.0, 1.0))
