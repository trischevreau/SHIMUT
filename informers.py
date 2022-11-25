"""
informers are displayers not meant to be construction bricks
"""

import tkinter as tk
import tkinter.ttk as ttk
import pychord

from VarPlus import StringVarPlus, BooleanVarPlus

from vars import *
from utils import *
import displayers
import converters


class IntersectionsPanel:
    """
    This class is meant to display intersections on the selected scale
    """

    def __init__(self, root, LM, player):
        """
        This builds the empty skeleton of the class
        :param root: the master frame to pack the elements to
        :param LM: the language manager
        """
        self.LM = LM
        self.player = player
        # Intersections
        jframe = ttk.Frame(root)
        pframe = ttk.LabelFrame(jframe, text=self.LM.get("parameters"))
        self.selected_number_to_find_SV = StringVarPlus(LM, "any")
        spinbox = ttk.Spinbox(pframe, from_=1, to=7, validate="key", state="readonly",
                                   textvariable=self.selected_number_to_find_SV, wrap=True)
        ttk.Button(pframe, command=self.__reapply, text=self.LM.get("apply")).grid(row=2, column=0)
        ttk.Label(pframe, text=self.LM.get("intersections_to_find")).grid(row=1, column=0)
        spinbox.grid(row=1, column=1)
        pframe.pack()
        self.score = displayers.Score(jframe, self.LM, self.player, 600, 200, 7)
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
        flattenened_scale = [i % 12 for i in scale]
        to_find = int(self.selected_number_to_find_SV.get_state())
        for scale_ in universe:
            n = 0
            for h in scale_[2]:
                if h % 12 in flattenened_scale:
                    n += 1
            if n == to_find:
                self.intersecting.append(scale_)
        to_apply_set = [[] for i in range(7)]
        to_apply_colors = [[] for i in range(7)]
        for y in range(len(self.intersecting)):
            elem = self.intersecting[y]
            elem[2] = [e % 12 for e in elem[2]]
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
        self.selected_number_to_find_SV.set(states[3])

    def get_state(self):
        return *self.score.get_state(), self.selected_number_to_find_SV.get_state()


class Chords:
    """
    This informer uses a score to display chords and their names.
    """

    def __init__(self, root, LM, player, lx, ly, n, func_to_apply=None):
        """
        This initializes external classes and creates the skeleton
        :param root: the master frame to pack the elements to
        :param player: the audio player
        :param lx: the horizontal length of the score
        :param ly: the vertical length of the score
        :param n: the number of notes that can be put on a score horizontally
        """
        self.LM = LM
        self.frame = ttk.Frame(root)
        if func_to_apply is None:
            self.func_to_apply = self.__reapply
        else:
            self.func_to_apply = func_to_apply
        self.score = displayers.Score(self.frame, LM, player, lx, ly, n, funct_to_apply=self.func_to_apply)
        self.deg_frame = ttk.LabelFrame(self.frame, text=LM.get("deg_of_chord"))
        self.deg_frame_checkboxes_SV = [BooleanVarPlus() for _ in range(n)]
        self.deg_frame_checkboxes = [ttk.Checkbutton(self.deg_frame, text=int_to_roman(i+1), command=self.func_to_apply,
                                                     variable=self.deg_frame_checkboxes_SV[i]) for i in range(n)]
        for elem in self.deg_frame_checkboxes:
            elem.pack(side="left")
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
        self.from_scale()
        self.score.apply(self.chords_list)
        self.display_chords_annotations()

    def set_state(self, states):
        translation, octave_number, alteration, *d = states
        self.score.selectedTranslationSV.set_state(translation)
        self.score.octave_number = int(octave_number)
        self.score.selected_alteration.set_state(alteration)
        for i in range(len(self.deg_frame_checkboxes_SV)):
            self.deg_frame_checkboxes_SV[i].set(bool(int(d[i])))

    def get_state(self):
        return self.score.selectedTranslationSV.get_state(), str(self.score.octave_number), \
               self.score.selected_alteration.get_state(), *[_.get_state() for _ in self.deg_frame_checkboxes_SV],


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
        self.chordsList = []
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
                self.chordsList.append(chord)
            else:
                self.chordsList.append([])
        self.score.apply(self.chordsList)
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
        translation, octave_number, alteration, *d = states
        self.score.selectedTranslationSV.set_state(translation)
        self.score.octave_number = int(octave_number)
        self.score.selected_alteration.set_state(alteration)
        for i in range(len(self.deg_frame_checkboxes_SV)):
            self.deg_frame_checkboxes_SV[i].set(bool(int(d[i])))
        for i in range(len(self.selected_chords_SV)):
            self.selected_chords_SV[i].set(d[len(self.deg_frame_checkboxes_SV) + i])
        self.selected_progression_SV.set_state(d[-1])

    def get_state(self):
        return self.score.selectedTranslationSV.get_state(), str(self.score.octave_number), \
               self.score.selected_alteration.get_state(), *[_.get_state() for _ in self.deg_frame_checkboxes_SV], \
               *[_.get_state() for _ in self.selected_chords_SV], self.selected_progression_SV.get_state()
