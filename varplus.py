from tkinter import StringVar, BooleanVar


class StringVarPlus(StringVar):

    def __init__(self, LM, type):
        self.LM = LM
        super().__init__()
        if type == "note":
            self.gfunc = self.LM.reverse_get_note
            self.sfunc = self.LM.get_note
        elif type == "text_db":
            self.gfunc = self.LM.reverse_get
            self.sfunc = self.LM.get
        elif type == "any":
            self.gfunc = str
            self.sfunc = str
        else:
            raise ValueError("Wrong StringVarPlus Type")

    def get_state(self):
        return self.gfunc(self.get())

    def set_state(self, v):
        self.set(self.sfunc(v))


class BooleanVarPlus(BooleanVar):

    def __init__(self):
        super().__init__()

    def get_state(self):
        return int(self.get())

    def set_state(self, v):
        self.set(bool(v))


class BooleanDictVarPlus:

    def __init__(self, n):
        self.n = n
        self.list_ = [BooleanVarPlus() for e in range(n)]

    def __len__(self):
        return self.n

    def __getitem__(self, item):
        return self.list_[item]

    def get_state(self):
        return [e.get_state() for e in self.list_]

    def set_state(self, states):
        assert self.n == len(states)
        for i in range(len(self.list_)):
            self.list_[i].set(states[i])
