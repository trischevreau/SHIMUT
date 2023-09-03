import tkinter as tk
from functools import partial
from tkinter import ttk as ttk

from tools.managers import MIDIFileWriter
from tools.converters import convert_height_to_midi

from tools.image import load_image
from varplus import StringVarPlus
from vars import all_notes, all_notes_extended


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
        self.colors = []
        self.LM = LM
        self.player = player
        self.func_to_apply = funct_to_apply
        self.frame = ttk.Frame(master)
        self.octave_number = 0
        self.delta = 0
        self.display_warning = False

        (self.width, self.height) = (lx, ly)
        self.annotations = ["" for _ in range(n)]
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
            "sol_clef": load_image("clef.png", int(self.line_delta * 4), int(self.line_delta * 8)),
            "note": load_image("note.png", int(self.line_delta * 1.2), int(0.9 * self.line_delta)),
            "warn": load_image("warn.png", int(self.line_delta * 2), int(2 * self.line_delta)),
        }

        """
        Parameters
        """

        pframe = ttk.Frame(self.frame)

        # alterations
        rframe = ttk.LabelFrame(pframe, text=self.LM.get("alteration"))
        self.selected_alteration = StringVarPlus(self.LM, "any")
        ttk.Radiobutton(rframe, text=self.LM.get("sharp"), variable=self.selected_alteration, value="#",
                        command=self.__reapply).pack(side="top")
        ttk.Radiobutton(rframe, text=self.LM.get("flat"), variable=self.selected_alteration, value="b",
                        command=self.__reapply).pack(side="top")
        rframe.pack(side="top")
        self.selected_alteration.set("#")

        # octaves
        o_frame = ttk.LabelFrame(pframe, text=self.LM.get("octaves"))
        ttk.Button(o_frame, text="+", width=3, command=self.__increment_octave).pack(side="right")
        ttk.Button(o_frame, text="-", width=3, command=self.__decrement_octave).pack(side="left")
        self.octave_label = ttk.Label(o_frame, text="0")
        self.octave_label.pack(side="left")
        o_frame.pack(side="top")

        # translation
        self.selected_translation_SV = StringVarPlus(self.LM, "note")
        translation_chooser = ttk.OptionMenu(pframe, self.selected_translation_SV, None,
                                             *self.LM.get_notes(all_notes.keys()), command=self.__reapply)
        ttk.Label(pframe, text=self.LM.get("translate_for")).pack(side="top")
        translation_chooser.pack(side="top")
        self.selected_translation_SV.set(self.LM.get_note("C"))

        # MIDI
        ttk.Button(pframe, text=self.LM.get("save_to_midi_file"), command=self.dump_to_midi_file).pack()

        pframe.pack(side="left")

        """
        Canvas
        """

        rframe = ttk.Frame(self.frame)
        self.canvas = tk.Canvas(rframe, width=lx, height=ly, bg="ivory")
        self.canvas.pack(side="top")

        """
        Playback
        """

        np_frame = ttk.LabelFrame(rframe, text=self.LM.get("play"))
        ttk.Button(np_frame, text=self.LM.get("all"), command=self.play_full).pack(side="left")
        for i in range(n):
            func = partial(self.play_pos, i)
            ttk.Button(np_frame, text=str(i+1), command=func).pack(side="left")
        np_frame.pack(side="bottom")
        rframe.pack(side="right")

        self.frame.pack(side="top")

    def set_state(self, states):
        translation, octave_number, alteration = states
        self.selected_translation_SV.set_state(translation)
        self.octave_number = int(octave_number)
        self.selected_alteration.set_state(alteration)

    def get_state(self):
        return self.selected_translation_SV.get_state(), self.octave_number, self.selected_alteration.get_state()

    def dump_to_midi_file(self):
        """
        Dumps the chord progression to a MIDI file.
        """
        midi_file_writer_ = MIDIFileWriter(self.LM)
        for chord in self.notes:
            midi_file_writer_.add_notes(1, [convert_height_to_midi(e - self.delta) for e in chord])
        midi_file_writer_.write_file()

    def __increment_octave(self):
        """
        Used as a callback function for the buttons that set the displayed octave.
        """
        self.octave_number += 1
        self.__reapply()

    def __decrement_octave(self):
        """
        Used as a callback function for the buttons that set the displayed octave.
        """
        self.octave_number -= 1
        self.__reapply()

    def play_pos(self, pos):
        """
        Plays the notes at a given position
        :param pos: the position on the score of the notes to play
        """
        self.player.play_note([self.notes[pos]])

    def play_full(self):
        """ Plays the full score """
        self.player.play_note([self.notes[pos] for pos in range(len(self.x_positions))])

    def do_initial(self):
        """
        This prints on the canvas everything that would be displayed no matter the notes, such as lines.
        It also deletes everything from before.
        """
        self.display_warning = False
        self.canvas.delete("all")
        self.canvas.create_image(self.padding * self.width * 1.5, self.height // 2,
                                 anchor=tk.CENTER, image=self.images["sol_clef"])
        self.annotations = ["" for _ in range(len(self.x_positions))]
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
            sa = self.selected_alteration.get()
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

    def display_note(self, n, xp, color="black"):
        """
        Displays a note on the score
        :param n: the height of the note
        :param xp: it's horizontal position (index) on the score
        :param color: the color of the note to display
        """
        (h, alt) = self.convert_height(n)
        # prints the note on the canvas
        if color == "black":
            self.canvas.create_image(self.x_positions[xp], self.height / 2 - (self.line_delta * (h / 2)),
                                     anchor=tk.CENTER, image=self.images["note"])
        else:
            lx, ly = (int(self.line_delta * 1.2), int(0.9 * self.line_delta))
            self.canvas.create_oval(self.x_positions[xp] - lx / 2,
                                    self.height / 2 - (self.line_delta * (h / 2)) - ly / 2,
                                    self.x_positions[xp] + lx / 2,
                                    self.height / 2 - (self.line_delta * (h / 2)) + ly / 2,
                                    fill=color)
        # prints the alteration on the canvas
        if alt != "n":
            self.canvas.create_text(self.x_positions[xp] - 1.2 * self.line_delta,
                                    self.height / 2 - self.line_delta * h / 2, fill=color,
                                    text=alt, font=("TkFixedFont", int(self.line_delta)))
        # prints additional lines if needed
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

    def apply(self, set_, colors="black"):
        """
        Applies a set of notes to the score, erasing what was on it before
        :param set_: the set of notes can be seen as a list of chords or as a list of single notes (noted in heights)
        :param colors: the colors of the notes (or one color for them all)
        """
        # fresh start
        assert len(set_) <= len(self.x_positions)
        if type(colors) == str:
            colors = [[colors for _ in range(len(set_[i]))] for i in range(len(set_))]
        self.notes = set_
        self.colors = colors
        self.do_initial()
        # transposition delta
        self.delta = all_notes_extended[self.LM.reverse_get_note(self.selected_translation_SV.get())]
        if self.delta > 6:  # this makes the scores more readable
            self.delta -= 12
        # iterating the notes
        for i in range(len(self.notes)):
            if type(self.notes[i]) == list:  # if it's chords ...
                for y in range(len(self.notes[i])):  # ... display each note
                    self.display_note(self.notes[i][y] - self.delta + self.octave_number * 12, i, self.colors[i][y])
            elif type(self.notes[i]) == int:  # if it's single notes ...
                # ... just display them
                self.display_note(self.notes[i] - self.delta + self.octave_number * 12, i, self.colors[i])
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
        self.octave_label.config(text=str(self.octave_number))

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

    def __reapply(self, *_):
        """ Used as a callback function when the transposition is changed to update the score and the classes using it
        :param _: completely ignored, the callback gives arguments that are not needed
        """
        self.apply(self.notes, self.colors)
        self.func_to_apply()
