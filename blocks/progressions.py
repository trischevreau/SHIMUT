import tkinter as tk
import tkinter.ttk as ttk
from functools import partial

from blocks.chords import Chords
from varplus import StringVarPlus

from vars import *
from tools.utils import *
from tools.image import load_image
from tools.managers import give_help

class Progressions(Chords):

    def __init__(self, root, LM, player, lx, ly, n):
        """
        Creates the skeleton of the chords progressions manager
        :param root: the root of the block
        :param LM: the language manager
        :param player: the midi player
        :param lx: the width of the score
        :param ly: the height of the score
        :param n: the number of available notes on the scores
        """
        super().__init__(root, LM, player, lx, ly, n, func_to_apply=self.__reapply)
        pframe = ttk.LabelFrame(root, text=self.LM.get("chord_progression_parameters"))
        self.selected_progression_SV = StringVarPlus(self.LM, "text_db")
        progression_chooser = ttk.OptionMenu(pframe, self.selected_progression_SV,
                                             self.LM.get("personalized"),
                                             *[self.LM.get(v) for v in progressions.keys()],
                                             command=self.__prog_changed)
        progression_chooser.grid(column=0, row=0)
        self.selected_chords_SV = []
        self.chords_selectors = []
        for i in range(n):
            self.selected_chords_SV.append(StringVarPlus(self.LM, "any"))
            self.chords_selectors.append(ttk.OptionMenu(pframe, self.selected_chords_SV[-1], int_to_roman(i + 1),
                                                        "", command=self.__chord_changed))
            self.chords_selectors[-1].grid(column=i + 1, row=0, padx=10, pady=10)
        ttk.Label(pframe, text=self.LM.get("classical_function")).grid(column=0, row=1)
        self.functions_colored_indicator = []
        for i in range(n):
            partial_func = partial(self.score.play_pos, i)
            self.functions_colored_indicator.append(tk.Button(pframe, text="   ", font="TkFixedFont", fg="black",
                                                              command=partial_func))
            self.functions_colored_indicator[-1].grid(column=i + 1, row=1, padx=10, pady=10)
        self.help_image = load_image("help.png", 15, 15)
        help_command = partial(give_help, "chord_functions", self.LM)
        ttk.Button(pframe, text="help", image=self.help_image, command=help_command).grid(column= n + 1, row=1)
        pframe.pack()

    def __reapply(self):
        """
        Applies the same chords once again.
        :return:
        """
        self.chords_list = []
        chords = [int_to_roman(v+1) for v in range(len(self.scale))]
        chords.extend([v + "/" for v in chords])
        chords.append("0")
        for i in range(0, len(self.chords_selectors)):
            val = int_to_roman(min(roman_to_int(self.selected_chords_SV[i].get().replace("/", "")), len(self.scale)))
            if "/" in self.selected_chords_SV[i].get():
                val += "/"
            self.chords_selectors[i].set_menu(val, *chords)
        for i in range(0, len(self.functions_colored_indicator)):
            self.functions_colored_indicator[i].config(text="   ", bg="white")
        for i in range(len(self.selected_chords_SV)):
            current = self.selected_chords_SV[i].get()
            if current != "0":
                for function, degrees in chord_functions.items():
                    if current in degrees:
                        self.functions_colored_indicator[i].config(bg=function_color[function],
                                                                   text=function_abbreviation[function])
                        break
                else:
                    self.functions_colored_indicator[i].config(bg=function_color["?"], text=" ? ")
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

    def __chord_changed(self, _):
        """
        Sets the selected progression according to what the user chose
        :param _: ignored (callback from tkinter)
        :return:
        """
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
        """
        Sets the option menu in accordance to the rest.
        :param prog:
        :return:
        """
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
