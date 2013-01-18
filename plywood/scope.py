

class Scope(object):
    def __init__(self, values):
        self.values = values
        self.restore_scope = [{}]
        self.delete_scope = [[]]

    def __setitem__(self, key):
        self.values.__setitem__(key)

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def push(self):
        pass

    def pop(self):
        pass
