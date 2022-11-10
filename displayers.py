"""
This file contains classes named "displayers".
They are elements meant to be used as elements of other classes if needed, but they can also be stand-alones.
Anyway they use a master container to be displayed on a root.
"""

from functools import partial

import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image

from vars import *
from utils import *


class Score:
    """ A score to display chords, and notes with annotations if needed.
    Most sizes are parametric, so it will be displayed according to the size assigned to it.
    """

    def __init__(self, master, LM, player, lx, ly, n, funct_to_apply=lambda: None):
        """
        The init class creates a more or less empty skeleton of it
        :param master: the master container on which everything will be packed
        :param lx: horizontal size of the score
        :param ly: vertical size of the score
        :param n: the number of notes that can be displayed horizontally
        """
        self.notes = []
        self.LM = LM
        self.player = player
        self.func_to_apply = funct_to_apply
        self.frame = ttk.Frame(master)
        self.display_warning = False
        pframe = ttk.Frame(self.frame)
        rframe = ttk.LabelFrame(pframe, text=self.LM.get("alteration"))
        self.selectedAlteration = tk.StringVar()
        ttk.Radiobutton(rframe, text=self.LM.get("sharp"), variable=self.selectedAlteration, value="#",
                        command=self.__reapply).pack(side="top")
        ttk.Radiobutton(rframe, text=self.LM.get("flat"), variable=self.selectedAlteration, value="b",
                        command=self.__reapply).pack(side="top")
        rframe.pack(side="top")
        self.octaveNumber = 0
        self.delta = 0
        oframe = ttk.LabelFrame(pframe, text=self.LM.get("octaves"))
        ttk.Button(oframe, text="+", width=3, command=self.__increment_octave).pack(side="right")
        ttk.Button(oframe, text="-", width=3, command=self.__decrement_octave).pack(side="left")
        self.octave_label = ttk.Label(oframe, text="0")
        self.octave_label.pack(side="left")
        oframe.pack(side="top")
        self.selectedTranslationSV = tk.StringVar()
        self.translationChooser = ttk.OptionMenu(pframe, self.selectedTranslationSV, None,
                                                 *self.LM.get_notes(all_notes.keys()), command=self.__reapply)
        ttk.Label(pframe, text=self.LM.get("translate_for")).pack(side="top")
        self.selectedTranslationSV.set(LM.get_note("C"))
        self.translationChooser.pack(side="top")
        pframe.pack(side="left")
        self.selectedAlteration.set("#")
        rframe = ttk.Frame(self.frame)
        self.canvas = tk.Canvas(rframe, width=lx, height=ly, bg="ivory")
        self.canvas.pack(side="top")
        npframe = ttk.LabelFrame(rframe, text=self.LM.get("play"))
        ttk.Button(npframe, text=self.LM.get("all"), command=self.__play_full).pack(side="left")
        for i in range(n):
            func = partial(self.__play_pos, i)
            ttk.Button(npframe, text=str(i+1), command=func).pack(side="left")
        npframe.pack(side="bottom")
        rframe.pack(side="right")
        self.frame.pack(side="top")
        (self.width, self.height) = (lx, ly)
        self.annotations = ["" for i in range(n)]
        self.padding = 0.1
        self.line_delta = self.height * (1 - self.padding * 2) / 10
        self.x_positions = [self.padding * self.width * 3
                            + (self.width * (1 - 5 * self.padding) / (n - 1)) * i for i in range(n)]
        self.convert_table = {
            -8: -12, -7: -11, -5: -10, -3: -9, -1: -8,
            0: -7, 2: -6, 4: -5, 5: -4, 7: -3, 9: -2, 11: -1,
            12: 0, 14: 1, 16: 2, 17: 3, 19: 4, 21: 5, 23: 6,
            24: 7, 26: 8, 28: 10
        }
        self.master = master
        self.images = {
            "sol_clef": self.__load_image("clef.png", int(self.line_delta * 4), int(self.line_delta * 8)),
            "note": self.__load_image("note.png", int(self.line_delta * 1.2), int(0.9 * self.line_delta)),
            "warn": self.__load_image("warn.png", int(self.line_delta * 2), int(2 * self.line_delta)),
        }

    def __load_image(self, file_name, lx, ly):
        return ImageTk.PhotoImage(
            Image.open("assets/"+file_name).convert("RGBA").resize((lx,ly)),
            master=self.master)

    def __increment_octave(self):
        """
        Used as a callback function for the buttons that set the displayed octave.
        """
        self.octaveNumber += 1
        self.__reapply()

    def __decrement_octave(self):
        """
        Used as a callback function for the buttons that set the displayed octave.
        """
        self.octaveNumber -= 1
        self.__reapply()

    def __play_pos(self, pos):
        """
        Plays the notes at a given position
        :param pos: the position on the score of the notes to play
        """
        self.player.play_note([self.notes[pos]])

    def __play_full(self):
        """ Plays the full score """
        for i in range(len(self.notes)):
            self.__play_pos(i)

    def do_initial(self):
        """
        This prints on the canvas everything that would be displayed no matter the notes, such as lines.
        It also deletes everything from before.
        """
        self.display_warning = False
        self.canvas.delete("all")
        self.canvas.create_image(self.padding * self.width * 1.5, self.height // 2,
                                 anchor=tk.CENTER, image=self.images["sol_clef"])
        self.annotations = ["" for i in range(len(self.x_positions))]
        for i in range(5):
            self.canvas.create_line(self.width * self.padding, self.height / 2 - (1.5 - i) * self.line_delta,
                                    self.width * (1 - self.padding), self.height / 2 - (1.5 - i) * self.line_delta,
                                    width=2, fill="black")

    def convert_height(self, n):
        """ This converts the height of the note to it's position on the lines
        :param n: the height of the note
        :return: it's position on the line and its alteration ('n' means none)
        """
        alt = "n"
        if (n % 12) in [1, 3, 6, 8, 10]:  # if the note is altered ...
            sa = self.selectedAlteration.get()
            # ... make it stick to the lines and write the alteration
            if sa == "#":
                n -= 1
            elif sa == "b":
                n += 1
            alt = sa
        # manages the (rare) case of the height being too high or too low for the convert_table
        while n < min(self.convert_table.keys()):
            n += 12
            self.display_warning = True
        while n > max(self.convert_table.keys()):
            n -= 12
            self.display_warning = True
        return self.convert_table[n], alt

    def display_note(self, n, xp):
        """
        Displays a note on the score
        :param n: the height of the note
        :param xp: it's horizontal position (index) on the score
        """
        (h, alt) = self.convert_height(n)
        # prints the note on the canvas
        self.canvas.create_image(self.x_positions[xp], self.height / 2 - (self.line_delta * (h / 2)),
                                 anchor=tk.CENTER, image=self.images["note"])
        # prints the alteration on the canvas
        if alt != "n":
            self.canvas.create_text(self.x_positions[xp] - 1.2 * self.line_delta,
                                    self.height / 2 - self.line_delta * h / 2,
                                    text=alt, font=("TkFixedFont", int(self.line_delta)))
        # prints additionnal lines if needed
        while h <= -6 or h >= 5:
            if abs(h) % 2 == 1:
                self.canvas.create_line(self.x_positions[xp] - self.line_delta,
                                        self.height / 2 - self.line_delta * h / 2,
                                        self.x_positions[xp] + self.line_delta,
                                        self.height / 2 - self.line_delta * h / 2,
                                        width=2, fill="black")
            if h < 0:
                h += 1
            else:
                h -= 1

    def apply(self, scale):
        """
        Apply a set of notes to the score
        :param scale: the set of notes can be seen as a list of chords or as a list of single notes (noted in heights)
        """
        assert len(scale) <= len(self.x_positions)
        self.notes = scale
        # fresh start
        self.do_initial()
        # transposition delta
        self.delta = all_notes_extended[self.LM.reverse_get_note(self.selectedTranslationSV.get())]
        if self.delta > 6:  # this helps not putting the notes too high
            self.delta -= 12
        # iterating the notes
        for i in range(len(self.notes)):
            if type(self.notes[i]) == list:  # if it's chords ...
                for e in self.notes[i]:  # ... display each note
                    self.display_note(e - self.delta + self.octaveNumber * 12, i)
            elif type(self.notes[i]) == int:  # if it's single notes ...
                self.display_note(self.notes[i] - self.delta + self.octaveNumber * 12, i)  # ... just display them
        # displaying annotations (chords name)
        for pos in range(len(self.annotations)):
            self.canvas.create_text(self.x_positions[pos], self.line_delta * (pos % 2 + 1),
                                    text=self.annotations[pos], font=("TkFixedFont", int(self.line_delta)))
        # warning
        if self.display_warning:
            self.canvas.create_image(self.width - self.images["warn"].width(),
                                     self.height - self.images["warn"].height(),
                                     anchor=tk.NW, image=self.images["warn"])
        # octave number
        self.octave_label.config(text=str(self.octaveNumber))

    def get_delta(self):
        """
        Returns the translation between reality and the score
        :return: delta, the translation
        """
        return self.delta

    def add_annotation(self, pos, annotation):
        """ Adds an annotation to the score
        :param pos: the horizontal index of the annotation
        :param annotation: the text of the annotation
        """
        assert pos <= len(self.x_positions)
        self.annotations[pos] = annotation
        self.canvas.create_text(self.x_positions[pos], self.line_delta * (pos % 2 + 1),
                                text=annotation, font=("TkFixedFont", int(self.line_delta*0.8)))

    def __reapply(self, *args):
        """ Used as a callback function when the transposition is changed to update the score and the classes using it
        :param args: completely ignored, the callback gives arguments that are not needed
        """
        self.apply(self.notes)
        self.func_to_apply()


class Keyboard:
    """ Mimics a keyboard to display a scale on it. """

    def __init__(self, master, LM):
        """ The init class creates a more or less empty skeleton of it
        :param master: the master container on which everything will be packed
        """
        self.LM = LM
        self.frame = ttk.LabelFrame(master, text=self.LM.get("keyboard"))
        self.kbNoteButtonsList = []
        for i in range(24):  # two octaves
            self.kbNoteButtonsList.append(tk.Button(self.frame, font="TkFixedFont", state=tk.DISABLED))
            if i % 12 in [0, 2, 4, 5, 7, 9, 11]:  # if it is a white key
                self.kbNoteButtonsList[-1].grid(column=i, row=1)
            else:  # if it is a black key
                self.kbNoteButtonsList[-1].grid(column=i, row=0)
        self.frame.pack(side="top")

    def initial_color(self):
        """ This takes back the keyboard to it's initial colors """
        for i in range(24):
            if i % 12 in [0, 2, 4, 5, 7, 9, 11]:
                x = "white"
            else:
                x = "black"
            self.kbNoteButtonsList[i].config(bg=x, text="   ")

    def apply(self, usable_notes):
        """
        Applies a scale to the keyboard.
        :param usable_notes: the notes to put on it
        """
        usable_notes = unoctaver(usable_notes)
        self.initial_color()
        for i in range(24):
            if i % 12 in usable_notes:
                deg = usable_notes.index(i % 12) + 1
                if deg == 1:
                    self.kbNoteButtonsList[i].config(bg="lightblue")
                else:
                    self.kbNoteButtonsList[i].config(bg="pink")
                self.kbNoteButtonsList[i].config(text=fill_spaces(int_to_roman(deg), 3))


class Guitar:
    """ This mimics a top view of a guitar to display the playable notes on it """

    def __init__(self, master, LM, tuning=("E", "A", "D", "G", "B", "E")):
        """ The init class creates a more or less empty skeleton of it
        :param master: the master container on which everything will be packed
        :param tuning: the initial tuning of the guitar
        """
        self.LM = LM
        self.frame = ttk.LabelFrame(master, text=self.LM.get("cords"))
        self.noteButtonsList = []
        self.selectedNotesSVList = []
        self.notesChoosers = []
        self.usableNotes = []
        for i in range(6):
            self.selectedNotesSVList.append(tk.StringVar())
            self.notesChoosers.append(tk.OptionMenu(self.frame, self.selectedNotesSVList[-1],
                                                    *self.LM.get_notes(all_notes.keys()), command=self.__reapply))
            self.notesChoosers[-1].grid(column=0, row=i)
            ttk.Label(self.frame, text="-").grid(column=1, row=i)
            self.selectedNotesSVList[-1].set(self.LM.get_note(tuning[5 - i]))
            temp = []
            for y in range(GUITAR_LENGTH - 1):
                temp.append(tk.Button(self.frame, font="TkFixedFont", state=tk.DISABLED))
                temp[-1].grid(column=1 + y, row=i)
            self.noteButtonsList.append(temp)
        for e in GUITAR_DOTS:
            if e[0] <= GUITAR_LENGTH:
                tk.Label(self.frame, text=e[1], font=("TkFixedFont", 16)).grid(column=e[0], row=7)
        self.frame.pack(side="top")

    def initial_color(self):
        """ This takes back the guitar to its initial colors """
        for e in self.noteButtonsList:
            for ee in e:
                ee.config(bg="white", text="   ")
        for e in self.notesChoosers:
            e.config(bg="white")

    def apply(self, scale_to_apply):
        """
        Applies a scale to the keyboard
        :param scale_to_apply: the notes to put on it
        """
        self.usableNotes = unoctaver(scale_to_apply)
        self.initial_color()
        for i in range(len(self.noteButtonsList)):
            for y in range(len(self.noteButtonsList[i]) + 1):
                n = (y + all_notes[self.LM.reverse_get_note(self.selectedNotesSVList[i].get())])
                if n % 12 in self.usableNotes:
                    deg = self.usableNotes.index(n % 12) + 1
                    if deg == 1:
                        color = "lightblue"
                    else:
                        color = "pink"
                    if y == 0:
                        self.notesChoosers[i].config(bg=color)
                    else:
                        self.noteButtonsList[i][y - 1].config(bg=color, text=fill_spaces(str(deg), 3))

    def __reapply(self, *arg):
        """ Used as a callback function when the transposition is changed to update the display
        :param arg: completely ignored, the callback gives arguments that are not needed
        """
        self.apply(self.usableNotes)
