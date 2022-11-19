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


class RelativeScales:
    """
    This class is meant to display relatives scales from the one selected
    """

    def __init__(self, root, LM):
        """
        This builds the empty skeleton of the class
        :param root: the master frame to pack the elements to
        """
        self.LM = LM
        self.frame = tk.LabelFrame(root, text="Gammes Relatives")
        self.selectedRelativeScaleSV = tk.Variable(value=[])
        self.relativesList = tk.Listbox(root, listvariable=self.selectedRelativeScaleSV, height=10,
                                        font=("TkFixedFont", 14))
        self.relativesList.pack(expand=True, fill=tk.BOTH)
        self.frame.pack()
        self.relatives = []

    def apply(self, scale):
        """
        This applies the selected scale to display its relative scales
        :param scale: the scale
        """
        self.relatives = relatives[tuple(sorted(unoctaver(scale)))]
        self.relativesList.delete(0, 'end')
        for e in self.relatives:
            self.relativesList.insert(0, self.LM.get_note(e[1])+" - "+self.LM.get(e[0]))


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
        self.chordsList = []
        self.scale = None
        self.player = player

    def from_scale(self):
        """
        Builds the chords list from the scale of the class
        """
        self.chordsList = []
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
            self.chordsList.append(chord)

    def display_chords_annotations(self):
        delta = self.score.get_delta()
        for i in range(len(self.chordsList)):
            # search which chord it is to display it. Sometimes chords have multiple names, hence the [0] index
            if self.chordsList[i] != []:
                try:
                    self.score.add_annotation(i, self.LM.get_note(str(pychord.find_chords_from_notes(
                        [converters.convert_height_to_english(h - delta) for h in self.chordsList[i]])[0])))
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
        self.score.apply(self.chordsList)
        self.display_chords_annotations()

    def set_state(self, states):
        translation, octave_number, alteration, *d = states
        self.score.selectedTranslationSV.set_state(translation)
        self.score.octaveNumber = int(octave_number)
        self.score.selectedAlteration.set_state(alteration)
        for i in range(len(self.deg_frame_checkboxes_SV)):
            self.deg_frame_checkboxes_SV[i].set(bool(int(d[i])))

    def get_state(self):
        return self.score.selectedTranslationSV.get_state(), str(self.score.octaveNumber),\
               self.score.selectedAlteration.get_state(), *[_.get_state() for _ in self.deg_frame_checkboxes_SV],


class Progressions(Chords):

    def __init__(self, root, LM, player, lx, ly, n):
        super().__init__(root, LM, player, lx, ly, n, func_to_apply=self.__reapply)
        self.pframe = ttk.LabelFrame(root, text=self.LM.get("chord_progression_parameters"))
        self.selected_progression = StringVarPlus(self.LM, "text_db")
        progression_chooser = ttk.OptionMenu(self.pframe, self.selected_progression,
                                             self.LM.get("personalized"),
                                             *[self.LM.get(v) for v in progressions.keys()],
                                             command=self.__prog_changed)
        progression_chooser.pack(side="left", expand=True, fill=tk.BOTH)
        self.selected_chords = []
        self.chords_selectors = []
        for i in range(n):
            self.selected_chords.append(StringVarPlus(self.LM, "any"))
            self.chords_selectors.append(ttk.OptionMenu(self.pframe, self.selected_chords[-1], int_to_roman(i+1),
                                                        "", command=self.__chord_changed))
            self.chords_selectors[-1].pack(side="left")
        self.pframe.pack()

    def __reapply(self):
        self.chordsList = []
        chords = [int_to_roman(v+1) for v in range(len(self.scale))]
        chords.extend([v + "/" for v in chords])
        chords.append("0")
        for i in range(0, len(self.chords_selectors)):
            val = int_to_roman(min(roman_to_int(self.selected_chords[i].get().replace("/", "")), len(self.scale)))
            if "/" in self.selected_chords[i].get():
                val += "/"
            self.chords_selectors[i].set_menu(val, *chords)
        for i in range(len(self.selected_chords)):
            current = self.selected_chords[i].get()
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
        t = [v.get() for v in self.selected_chords]
        for k, v in progressions.items():
            v.extend(["0" for _ in range(len(t) - len(v))])
            if v == t:
                self.selected_progression.set(self.LM.get(k))
                found = True
        if not found:
            self.selected_progression.set(self.LM.get("personalized"))
        self.__reapply()

    def __prog_changed(self, prog):
        p = progressions[self.LM.reverse_get(prog)]
        p.extend(["0" for _ in range(len(self.selected_chords) - len(p))])
        for i in range(len(p)):
            self.selected_chords[i].set(p[i])
        self.__reapply()

    def set_state(self, states):
        translation, octave_number, alteration, *d = states
        self.score.selectedTranslationSV.set_state(translation)
        self.score.octaveNumber = int(octave_number)
        self.score.selectedAlteration.set_state(alteration)
        for i in range(len(self.deg_frame_checkboxes_SV)):
            self.deg_frame_checkboxes_SV[i].set(bool(int(d[i])))
        for i in range(len(self.selected_chords)):
            self.selected_chords[i].set(d[len(self.deg_frame_checkboxes_SV)+i])
        self.selected_progression.set_state(d[-1])

    def get_state(self):
        return self.score.selectedTranslationSV.get_state(), str(self.score.octaveNumber),\
               self.score.selectedAlteration.get_state(), *[_.get_state() for _ in self.deg_frame_checkboxes_SV],\
               *[_.get_state() for _ in self.selected_chords], self.selected_progression.get_state()
