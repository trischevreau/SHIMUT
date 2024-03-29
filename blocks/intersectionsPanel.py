import tkinter as tk
from tkinter import ttk as ttk
from random import choice

import blocks.score
from tools.utils import int_to_roman
from varplus import StringVarPlus, BooleanVarPlus
from vars import universe, colors


class IntersectionsPanel:
    """
    This class is meant to display intersections on the selected scale
    """

    def __init__(self, root, language_manager, player, lw, lh):
        """
        This builds the empty skeleton of the class
        :param root: the master frame to pack the elements to
        :param language_manager: the language manager
        :param player: the midi player
        :param lw: the width of the score
        :param lh: the height of the score
        """
        self.LM = language_manager
        self.player = player
        self.root = root
        self.scale = []
        self.note = None
        self.usable_scales = []
        # Intersections
        j_frame = ttk.Frame(root)
        pframe = ttk.LabelFrame(j_frame, text=self.LM.get("parameters"))
        self.selected_number_to_find_SV = StringVarPlus(language_manager, "any")
        ttk.Label(pframe, text=self.LM.get("intersections_to_find")).grid(row=0, column=0)
        self.check_buttons_SV = [BooleanVarPlus() for _ in range(7)]
        bframe = ttk.Frame(pframe)
        self.check_buttons = [
            ttk.Checkbutton(bframe, text=int_to_roman(i+1), command=self.__reapply,
                            variable=self.check_buttons_SV[i]) for i in range(7)
        ]
        for i in range(len(self.check_buttons)):
            self.check_buttons_SV[i].set(False)
            self.check_buttons[i].grid(column=1+i, row=0)
        bframe.grid(row=0, column=1)
        self.same_starting_note_SV = BooleanVarPlus()
        ttk.Checkbutton(pframe, text=self.LM.get("same_starting_note"), command=self.__reapply,
                        variable=self.same_starting_note_SV).grid(row=1, column=0)
        self.same_scale_size_SV = BooleanVarPlus()
        ttk.Checkbutton(pframe, text=self.LM.get("same_scale_size"), command=self.__reapply,
                        variable=self.same_scale_size_SV).grid(row=1, column=1)
        pframe.pack()
        self.score = blocks.score.Score(j_frame, self.LM, self.player, lw, lh, 7)
        self.selected_scale_SV = tk.Variable(value=[])
        self.intersections_list = tk.Listbox(j_frame, listvariable=self.selected_scale_SV, height=10,
                                             font=("TkFixedFont", 12))
        scrollbar = ttk.Scrollbar(j_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.intersections_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.intersections_list.yview)
        self.intersections_list.pack(expand=True, fill=tk.BOTH)
        j_frame.pack(expand=True, fill=tk.BOTH)
        self.intersecting = []

    def apply(self, scale, note, usable_scales):
        """
        This applies the selected scale to display its intersections
        :param scale: the scale
        :param note: the starting note of the scale
        :param usable_scales: the set of scales to search for intersections in
        """
        # init variables
        self.intersecting = []
        self.intersections_list.delete(0, 'end')
        self.scale = scale
        self.note = note
        self.usable_scales = usable_scales
        flattened_scale = [e % 12 for e in scale]
        # configure the check buttons
        for i in range(len(self.check_buttons)):
            if i >= len(flattened_scale):
                self.check_buttons[i].config(state=tk.DISABLED)
            else:
                self.check_buttons[i].config(state=tk.NORMAL)
        # notes to find
        to_find = [flattened_scale[i] for i in range(7)
                   if (self.check_buttons_SV[i].get() and i < len(flattened_scale))]
        # search for the sets that are correctly 'intersecting'
        same_starting_note = self.same_starting_note_SV.get()
        same_scale_size = self.same_scale_size_SV.get()
        for scale_ in universe:
            scale_[2] = [e % 12 for e in scale_[2]]
            if set.issubset(set(to_find), set(scale_[2])):
                if (not same_scale_size) or (same_scale_size and len(scale_[2]) == len(flattened_scale)):
                    if (not same_starting_note) or (same_starting_note and scale_[2][0] == flattened_scale[0]):
                        self.intersecting.append(scale_)
        # get rid of the exact same scale
        for y in range(len(self.intersecting)):
            elem = self.intersecting[y]
            if elem[2] == flattened_scale and elem[1] == self.note:
                self.intersecting.pop(y)
                break
        # display it
        to_apply_set = [[] for _ in range(7)]
        to_apply_colors = [[] for _ in range(7)]
        used_colors = []
        self.intersections_list.config(state=tk.NORMAL)
        for y in range(len(self.intersecting)):
            elem = self.intersecting[y]
            scores = []
            l, l_ = len(elem[2]), len(flattened_scale)
            for d in range(len(elem[2])):
                scores.append((sum([elem[2][(d+i) % l] == flattened_scale[i % l_] for i in range(len(elem[2]))]), d))
            scores.sort(key=lambda z: z[0])
            d = scores[-1][1]
            if elem[0] in self.usable_scales:
                cont = 0
                color = "white"
                while cont < len(colors):
                    if sum([c for c in self.root.winfo_rgb(color)]) < 2 * 65535 and color not in used_colors:
                        used_colors.append(color)
                        break
                    else:
                        cont += 1
                        color = choice(colors)
                for i in range(len(elem[2])):
                    to_apply_set[i].append(elem[2][(d + i) % len(elem[2])])
                    to_apply_colors[i].append(color)
                self.intersections_list.insert(0, self.LM.get_note(elem[1]) + " - " + self.LM.get(elem[0]))
                self.intersections_list.itemconfig(0, {'fg': color})
        for i in range(len(flattened_scale)):
            to_apply_set[i].append(flattened_scale[i])
            to_apply_colors[i].append("black")
        self.score.apply(to_apply_set, to_apply_colors)

    def __reapply(self, *_):
        """ Applies the scale, note and usable_scale once again. """
        self.apply(self.scale, self.note, self.usable_scales)

    def set_state(self, states):
        self.score.set_state(states[0:3])
        self.same_starting_note_SV.set(states[3])
        self.same_scale_size_SV.set(states[4])
        for i in range(len(self.check_buttons)):
            self.check_buttons_SV[i].set(states[5+i])

    def get_state(self):
        return *self.score.get_state(), self.same_starting_note_SV.get_state(), self.same_scale_size_SV.get_state(), \
               *[self.check_buttons_SV[i].get_state() for i in range(len(self.check_buttons_SV))]
