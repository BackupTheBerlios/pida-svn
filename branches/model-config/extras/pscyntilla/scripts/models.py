
class Function:
    def __init__(self, name, ret_type, args, id):
        self.name = name
        self.ret_type = ret_type
        self.args = args
        self.id = id
        self.vals = (name, ret_type, args, id)

    def __getitem__(self, key):
        return self.vals[key]