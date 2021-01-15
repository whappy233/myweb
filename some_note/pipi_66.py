from functools import partial
class F(partial):
    def __xxx__(self, other):
        if isinstance(other,tuple):
            return self(*other)
        return self(other)