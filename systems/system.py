class System(object):
    def __init__(self, engine):
        self.engine = engine
        self.callbacks = {}
        self.settings = {'enabled': True}

        self.paused = False

    def get_settings(self, path=()):
        pathstr = '/'.join(path)
        settings = []
        directories = []
        for k, v in sorted(self.settings.iteritems(), key=lambda i: i[0]):
            if k.startswith(pathstr):
                local = k.split('/')[len(path):]
                if len(local) > 1:
                    if local[0] not in directories:
                        directories.append(local[0])
                else:
                    settings.append((local[0], v))

        return settings, directories

    def on_pause(self, paused):
        self.paused = paused

    def __repr__(self):
        return self.__class__.__name__
