(TAG,  # int
 POS,  # glm.vec3
 ANGLE,  # float
 INPUT,  # glm.vec2
 ANIMATOR,  # Animator
 SHOOT,  # bool
 VEHICLE,  # entity
 SIZE,  # glm.vec2
 VEL,  # glm.vec3
 DAMPING,  # float
 GRAVITY,  # float
 FORCE,  # glm.vec3
 FRICTION,  # float
 MESH,  # str
 TEX,  # str
 TEX_ID,  # int
 FBO_TEX,  # int
 BUTTON,  # (CALLBACK (int), ARGS (tuple))
 STATE,  # str
 MOVE_SPEED,  # float
 JUMP,  # float
 CAM_OFFSET,  # glm.vec3
 ANIM,  # (TIMER (float), ANIMATION (int))
 TEXT,  # str
 COLOR,  # tuple (float)
 ) = range(25)

# TAGS
GUI_TAG, PLAYER_TAG = range(2)


def has_components(e, components):
    for c in components:
        if c not in e:
            return False
    return True


def has_tag(e, tag):
    if TAG in e:
        return e[TAG] is tag
