import tkinter as tk
import tkinter.ttk as ttk

from varplus import StringVarPlus

from vars import *
from tools.utils import *


class Guitar:
    """ This mimics a top view of a guitar to display the playable notes on it """

    def __init__(self, master, LM):
        """ The init class creates a more or less empty skeleton of it
        :param master: the master container on which everything will be packed
        :param LM: the language manager
        """
        self.LM = LM
        self.frame = ttk.LabelFrame(master, text=self.LM.get("cords"))
        self.note_buttons = []
        self.selected_notes_SV = []
        self.notes_choosers = []
        self.usable_notes = []
        for i in range(6):
            self.selected_notes_SV.append(StringVarPlus(self.LM, "note"))
            self.notes_choosers.append(tk.OptionMenu(self.frame, self.selected_notes_SV[-1],
                                                     *self.LM.get_notes(all_notes.keys()), command=self.__reapply))
            self.notes_choosers[-1].grid(column=0, row=i)
            ttk.Label(self.frame, text="-").grid(column=1, row=i)
            temp = []
            for y in range(GUITAR_LENGTH - 1):
                temp.append(tk.Button(self.frame, font="TkFixedFont", state=tk.DISABLED))
                temp[-1].grid(column=1 + y, row=i)
            self.note_buttons.append(temp)
        for e in GUITAR_DOTS:
            if e[0] <= GUITAR_LENGTH:
                tk.Label(self.frame, text=e[1], font=("TkFixedFont", 16)).grid(column=e[0], row=7)
        self.frame.pack(side="top")
        self.instrument = None

    def initial_color(self):
        """ This takes back the guitar to its initial colors """
        for e in self.note_buttons:
            for ee in e:
                ee.config(bg="white", text="   ")
        for e in self.notes_choosers:
            e.config(bg="white")

    def apply(self, scale_to_apply):
        """
        Applies a scale to the guitar
        :param scale_to_apply: the notes to put on it
        """
        self.usable_notes = unoctaver(scale_to_apply)
        self.initial_color()
        for i in range(len(self.note_buttons)):
            for y in range(len(self.note_buttons[i]) + 1):
                n = (y + all_notes[self.LM.reverse_get_note(self.selected_notes_SV[i].get())])
                if n % 12 in self.usable_notes:
                    deg = self.usable_notes.index(n % 12) + 1
                    if deg == 1:
                        color = "lightblue"
                    else:
                        color = "pink"
                    if y == 0:
                        self.notes_choosers[i].config(bg=color)
                    else:
                        self.note_buttons[i][y - 1].config(bg=color, text=fill_spaces(str(deg), 3))

    def __reapply(self, *_):
        """ Used as a callback function when the transposition is changed to update the display
        :param _: completely ignored, the callback gives arguments that are not needed
        """
        self.apply(self.usable_notes)

    def set_state(self, states):
        for i in range(len(states)):
            self.selected_notes_SV[i].set_state(states[i])

    def get_state(self):
        return [_.get_state() for _ in self.selected_notes_SV]
