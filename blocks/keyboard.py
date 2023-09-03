import tkinter as tk
from tkinter import ttk as ttk

from tools.utils import un_octaver, fill_spaces, int_to_roman


class Keyboard:
    """ Mimics a keyboard to display a scale on it. """

    def __init__(self, master, LM):
        """ The init class creates a more or less empty skeleton of it
        :param master: the master container on which everything will be packed
        :param LM: the language manager
        """
        self.LM = LM
        self.frame = ttk.LabelFrame(master, text=self.LM.get("keyboard"))
        self.kb_note_buttons = []
        for i in range(24):  # two octaves
            self.kb_note_buttons.append(tk.Button(self.frame, font="TkFixedFont", state=tk.DISABLED))
            if i % 12 in [0, 2, 4, 5, 7, 9, 11]:  # if it is a white key
                self.kb_note_buttons[-1].grid(column=i, row=1)
            else:  # if it is a black key
                self.kb_note_buttons[-1].grid(column=i, row=0)
        self.frame.pack(side="top")

    def initial_color(self):
        """ This takes back the keyboard to it's initial colors """
        for i in range(24):
            if i % 12 in [0, 2, 4, 5, 7, 9, 11]:
                x = "white"
            else:
                x = "black"
            self.kb_note_buttons[i].config(bg=x, text="   ")

    def apply(self, usable_notes):
        """
        Applies a scale to the keyboard.
        :param usable_notes: the notes to put on it
        """
        usable_notes = un_octaver(usable_notes)
        self.initial_color()
        for i in range(24):
            if i % 12 in usable_notes:
                deg = usable_notes.index(i % 12) + 1
                if deg == 1:
                    self.kb_note_buttons[i].config(bg="lightblue")
                else:
                    self.kb_note_buttons[i].config(bg="pink")
                self.kb_note_buttons[i].config(text=fill_spaces(int_to_roman(deg), 3))
