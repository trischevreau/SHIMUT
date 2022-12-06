import tkinter as tk
from tkinter import ttk as ttk

import blocks.score
from tools.utils import int_to_roman
from varplus import StringVarPlus, BooleanVarPlus
from vars import universe


class IntersectionsPanel:
    """
    This class is meant to display intersections on the selected scale
    """

    def __init__(self, root, language_manager, player, lw, lh):
        """
        This builds the empty skeleton of the class

        :param root: the master frame to pack the elements to
        :param language_manager: the language manager
        """
        self.LM = language_manager
        self.player = player
        # Intersections
        jframe = ttk.Frame(root)
        pframe = ttk.LabelFrame(jframe, text=self.LM.get("parameters"))
        self.selected_number_to_find_SV = StringVarPlus(language_manager, "any")
        ttk.Button(pframe, command=self.__reapply, text=self.LM.get("apply")).grid(row=2, column=0)
        ttk.Label(pframe, text=self.LM.get("intersections_to_find")).grid(row=0, column=0)
        self.check_buttons_SV = [BooleanVarPlus() for i in range(7)]
        self.check_buttons = [
            ttk.Checkbutton(pframe, text=int_to_roman(i+1), command=self.__reapply,
                            variable=self.check_buttons_SV[i]) for i in range(7)
        ]
        for i in range(len(self.check_buttons)):
            self.check_buttons_SV[i].set(False)
            self.check_buttons[i].grid(column=1+i, row=0)
        pframe.pack()
        self.score = blocks.score.Score(jframe, self.LM, self.player, lw, lh, 7)
        self.selected_scale_SV = tk.Variable(value=[])
        self.intersections_list = tk.Listbox(jframe, listvariable=self.selected_scale_SV, height=10,
                                             font=("TkFixedFont", 12))
        scrollbar = ttk.Scrollbar(jframe)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.intersections_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.intersections_list.yview)
        self.intersections_list.pack(expand=True, fill=tk.BOTH)
        jframe.pack(expand=True, fill=tk.BOTH)
        self.intersecting = []

    def apply(self, scale, note, usable_scales):
        """
        This applies the selected scale to display its intersections
        :param scale: the scale
        """
        self.intersecting = []
        self.intersections_list.delete(0, 'end')
        self.scale = scale
        self.note = note
        self.usable_scales = usable_scales
        colors = ["red", "blue", "green", "magenta", "cyan", "orange"]
        flattenened_scale = [e % 12 for e in scale]
        to_find = [flattenened_scale[i] for i in range(7)
                   if (self.check_buttons_SV[i].get() and i < len(flattenened_scale))]
        for i in range(len(self.check_buttons)):
            if i >= len(flattenened_scale):
                self.check_buttons[i].config(state=tk.DISABLED)
            else:
                self.check_buttons[i].config(state=tk.NORMAL)
        for scale_ in universe:
            scale_[2] = [e % 12 for e in scale_[2]]
            if set.issubset(set(to_find), set(scale_[2])):
                self.intersecting.append(scale_)
        to_apply_set = [[] for i in range(7)]
        to_apply_colors = [[] for i in range(7)]
        for y in range(len(self.intersecting)):
            elem = self.intersecting[y]
            scores = []
            d = 0
            l, l_ = len(elem[2]), len(flattenened_scale)
            for d in range(len(elem[2])):
                scores.append((sum([elem[2][(d+i) % l] == flattenened_scale[i % l_] for i in range(len(elem[2]))]),
                               d))
            scores.sort(key=lambda z: z[0])
            d = scores[-1][1]
            if elem[0] in self.usable_scales:
                for i in range(len(elem[2])):
                    to_apply_set[i].append(elem[2][(d + i) % len(elem[2])])
                    to_apply_colors[i].append(colors[y % len(colors)])
                self.intersections_list.insert(0, self.LM.get_note(elem[1]) + " - " + self.LM.get(elem[0]))
                self.intersections_list.itemconfig(0, {'fg': colors[y % len(colors)]})
        for i in range(len(flattenened_scale)):
            to_apply_set[i].append(flattenened_scale[i])
            to_apply_colors[i].append("black")
        self.score.apply(to_apply_set, to_apply_colors)

    def __reapply(self):
        self.apply(self.scale, self.note, self.usable_scales)

    def set_state(self, states):
        self.score.set_state(states[0:3])
        for i in range(len(self.check_buttons)):
            self.check_buttons_SV[i].set(states[3+i])

    def get_state(self):
        return *self.score.get_state(),\
               *[self.check_buttons_SV[i].get_state() for i in range(len(self.check_buttons_SV))]
