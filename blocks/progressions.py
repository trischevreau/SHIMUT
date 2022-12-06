"""
informers are displayers not meant to be construction bricks
"""

import tkinter as tk
import tkinter.ttk as ttk

from blocks.chords import Chords
from varplus import StringVarPlus

from vars import *
from tools.utils import *


class Progressions(Chords):

    def __init__(self, root, LM, player, lx, ly, n):
        super().__init__(root, LM, player, lx, ly, n, func_to_apply=self.__reapply)
        pframe = ttk.LabelFrame(root, text=self.LM.get("chord_progression_parameters"))
        self.selected_progression_SV = StringVarPlus(self.LM, "text_db")
        progression_chooser = ttk.OptionMenu(pframe, self.selected_progression_SV,
                                             self.LM.get("personalized"),
                                             *[self.LM.get(v) for v in progressions.keys()],
                                             command=self.__prog_changed)
        progression_chooser.pack(side="left", expand=True, fill=tk.BOTH)
        self.selected_chords_SV = []
        self.chords_selectors = []
        for i in range(n):
            self.selected_chords_SV.append(StringVarPlus(self.LM, "any"))
            self.chords_selectors.append(ttk.OptionMenu(pframe, self.selected_chords_SV[-1], int_to_roman(i + 1),
                                                        "", command=self.__chord_changed))
            self.chords_selectors[-1].pack(side="left")
        pframe.pack()

    def __reapply(self):
        self.chords_list = []
        chords = [int_to_roman(v+1) for v in range(len(self.scale))]
        chords.extend([v + "/" for v in chords])
        chords.append("0")
        for i in range(0, len(self.chords_selectors)):
            val = int_to_roman(min(roman_to_int(self.selected_chords_SV[i].get().replace("/", "")), len(self.scale)))
            if "/" in self.selected_chords_SV[i].get():
                val += "/"
            self.chords_selectors[i].set_menu(val, *chords)
        for i in range(len(self.selected_chords_SV)):
            current = self.selected_chords_SV[i].get()
            if current != "0":
                inverted = False
                chord = []
                oct_sup = 0
                for ii in range(0, len(self.deg_frame_checkboxes_SV)):
                    if self.deg_frame_checkboxes_SV[ii].get():
                        if "/" in current:
                            inverted = True
                            current = current.replace("/", "")
                        index = (roman_to_int(current) - 1 + ii) % len(self.scale)
                        if len(chord) > 0:
                            while self.scale[index] + 12 * oct_sup < chord[-1]:
                                oct_sup += 1
                        chord.append(self.scale[index] + 12 * oct_sup)
                if inverted:
                    chord = chord[1:] + [chord[0] + 12]
                self.chords_list.append(chord)
            else:
                self.chords_list.append([])
        self.score.apply(self.chords_list)
        self.display_chords_annotations()

    def __chord_changed(self, chord):
        found = False
        t = [v.get() for v in self.selected_chords_SV]
        for k, v in progressions.items():
            v.extend(["0" for _ in range(len(t) - len(v))])
            if v == t:
                self.selected_progression_SV.set(self.LM.get(k))
                found = True
        if not found:
            self.selected_progression_SV.set(self.LM.get("personalized"))
        self.__reapply()

    def __prog_changed(self, prog):
        p = progressions[self.LM.reverse_get(prog)]
        p.extend(["0" for _ in range(len(self.selected_chords_SV) - len(p))])
        for i in range(len(p)):
            self.selected_chords_SV[i].set(p[i])
        self.__reapply()

    def set_state(self, states):
        _, _, _, *d = states
        self.score.set_state(states[0:3])
        for i in range(len(self.deg_frame_checkboxes_SV)):
            self.deg_frame_checkboxes_SV[i].set(bool(int(d[i])))
        for i in range(len(self.selected_chords_SV)):
            self.selected_chords_SV[i].set(d[len(self.deg_frame_checkboxes_SV) + i])
        self.selected_progression_SV.set_state(d[-1])

    def get_state(self):
        return *self.score.get_state(), *[_.get_state() for _ in self.deg_frame_checkboxes_SV], \
               *[_.get_state() for _ in self.selected_chords_SV], self.selected_progression_SV.get_state()
