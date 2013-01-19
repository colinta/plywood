

class Scope(object):
    def __init__(self, values=None):
        if values is None:
            self.values = {}
        else:
            self.values = values
        self.restore_scope = [{}]
        self.delete_scope = [[]]

    def tracking(self, key):
        return key in self.delete_scope[-1] and key in self.restore_scope[-1]

    def track(self, key):
        if key in self.values:
            self.restore_scope[-1][key] = self.values[key]
        else:
            self.delete_scope[-1].append(key)

    def __setitem__(self, key, value):
        if not self.tracking(key):
            self.track(key)
        self.values.__setitem__(key, value)

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __getattr__(self, attr):
        try:
            return self.values.__getattribute__(attr)
        except AttributeError:
            return self.values[attr]

    def __contains__(self, attr):
        return self.values.__contains__(attr)

    def push(self):
        self.restore_scope.append({})
        self.delete_scope.append([])

    def pop(self):
        restore = self.restore_scope.pop()
        delete = self.delete_scope.pop()
        for key, value in restore.iteritems():
            self.values[key] = value
        for key in delete:
            del self.values[key]
