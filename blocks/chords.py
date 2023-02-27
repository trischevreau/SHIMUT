import tkinter as tk
from tkinter import ttk as ttk

import pychord

import blocks.score
from tools import converters
from tools.utils import int_to_roman
from varplus import BooleanVarPlus


class Chords:
    """
    This informer uses a score to display chords and their names.
    """

    def __init__(self, root, LM, player, lx, ly, n, func_to_apply=None):
        """
        This initializes external classes and creates the skeleton
        :param root: the master frame to pack the elements to
        :param LM: the language manager
        :param player: the audio player
        :param lx: the horizontal length of the score
        :param ly: the vertical length of the score
        :param n: the number of notes that can be put on a score horizontally
        :param func_to_apply: the function to call each time the score changes.
        """
        self.LM = LM
        self.frame = ttk.Frame(root)
        if func_to_apply is None:
            self.func_to_apply = self.__reapply
        else:
            self.func_to_apply = func_to_apply
        self.score = blocks.score.Score(self.frame, LM, player, lx, ly, n, funct_to_apply=self.func_to_apply)
        self.deg_frame = ttk.LabelFrame(self.frame, text=LM.get("deg_of_chord"))
        self.deg_frame_checkboxes_SV = [BooleanVarPlus() for _ in range(n)]
        self.deg_frame_checkboxes = [ttk.Checkbutton(self.deg_frame, text=int_to_roman(i+1), command=self.func_to_apply,
                                                     variable=self.deg_frame_checkboxes_SV[i]) for i in range(n)]
        for elem in self.deg_frame_checkboxes:
            elem.pack(side="left", fill=tk.BOTH)
        self.deg_frame.pack()
        self.frame.pack()
        self.chords_list = []
        self.scale = None
        self.player = player

    def from_scale(self):
        """
        Builds the chords list from the scale of the class
        """
        self.chords_list = []
        oct_sup = 0
        for starting_note in range(len(self.scale)):
            chord = []
            oct_sup = 0
            for i in range(0, len(self.deg_frame_checkboxes_SV)):
                if self.deg_frame_checkboxes_SV[i].get():
                    index = (starting_note + i) % len(self.scale)
                    if len(chord) > 0:
                        while self.scale[index] + 12 * oct_sup < chord[-1]:
                            oct_sup += 1
                    chord.append(self.scale[index] + 12 * oct_sup)
            self.chords_list.append(chord)

    def display_chords_annotations(self):
        """
        Displays chords annotations.
        :return:
        """
        delta = self.score.get_delta()
        for i in range(len(self.chords_list)):
            # search which chord it is to display it. Sometimes chords have multiple names, hence the [0] index
            if self.chords_list[i] != []:
                try:
                    self.score.add_annotation(i, self.LM.get_note(str(pychord.find_chords_from_notes(
                        [converters.convert_height_to_english(h - delta) for h in self.chords_list[i]])[0])))
                except IndexError:
                    self.score.add_annotation(i, "-")

    def apply(self, scale):
        """
        Applies the scale to the class
        :param scale: the scale to apply
        """
        self.scale = scale
        for i in range(0, len(self.score.x_positions)):
            if i < len(self.scale):
                self.deg_frame_checkboxes[i].config(state=tk.ACTIVE)
            else:
                self.deg_frame_checkboxes[i].config(state=tk.DISABLED)
                self.deg_frame_checkboxes_SV[i].set(False)
        self.func_to_apply()

    def __reapply(self):
        """ Applies everything once again. """
        self.from_scale()
        self.score.apply(self.chords_list)
        self.display_chords_annotations()

    def set_state(self, states):
        _, _, _, *d = states
        self.score.set_state(states[0:3])
        for i in range(len(self.deg_frame_checkboxes_SV)):
            self.deg_frame_checkboxes_SV[i].set(bool(int(d[i])))

    def get_state(self):
        return *self.score.get_state(), *[_.get_state() for _ in self.deg_frame_checkboxes_SV],
