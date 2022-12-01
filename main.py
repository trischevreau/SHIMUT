import tkinter as tk
from tkinter import filedialog as fd
from random import choice
import tkinter.ttk as ttk
import os
import pathlib
from functools import partial

from varplus import StringVarPlus, BooleanVarPlus, BooleanDictVarPlus

import managers
import displayers
import informers
from vars import *
from utils import *


class Main:

    def __init__(self, to_load="parameters/default.SHIMUTstate"):
        """
        This creates the skeleton of the interface
        :param lang: the language of the software
        :param conv: the notation to use to display the notes
        """

        self.root = tk.Tk()

        # Classes init 1
        self.param_reader = managers.ParamReader()
        self.param_reader.load(to_load)
        self.LM = managers.LanguageManager(self.param_reader.get("lang_SV"), self.param_reader.get("conv_SV"))

        # Variable init
        self.scale = []
        self.lang_SV = StringVarPlus(self.LM, "any")
        self.conv_SV = StringVarPlus(self.LM, "any")
        self.chosen_scales = BooleanDictVarPlus(len(sg.__dict__))
        self.choosable_scales_names = [e[1] for e in sg.__dict__.items()]
        self.usable_scales = []

        # Classes init 2
        self.player = managers.Player(0, 127, 0.2)
        self.menubar = tk.Menu(self.root)
        self.main_notebook = ttk.Notebook(self.root)

        """
        Parameters
        """

        # Parameter frames
        parameters_frame = ttk.Frame(self.root)
        scale_parameters_frame = ttk.LabelFrame(parameters_frame, text=self.LM.get("scale_parameters"),
                                                     name="params")
        # Scale Type
        self.selected_scale_type_SV = StringVarPlus(self.LM, "text_db")
        self.scale_chooser = ttk.OptionMenu(scale_parameters_frame, self.selected_scale_type_SV, None,
                                           *[self.LM.get(elem) for elem in scales.keys()], command=self.__update_notes)
        self.scale_chooser.pack(side="right")

        # Scale height
        self.usable_scale_notes = []
        self.selected_scale_note_SV = StringVarPlus(self.LM, "note")
        self.note_chooser = ttk.OptionMenu(scale_parameters_frame, self.selected_scale_note_SV, None)
        self.note_chooser["menu"].delete(0, "end")
        self.note_chooser.pack(side="left")

        scale_parameters_frame.grid(row=0, column=0)

        # Apply Button
        ttk.Button(parameters_frame, text=self.LM.get("apply"), command=self.apply).grid(row=0, column=3)

        parameters_frame.pack()

        """
        Notebook Display
        """

        self.main_notebook.pack(expand=True)

        # Display of instruments
        instruments_display_frame = ttk.Frame(self.main_notebook)
        self.keyboard = displayers.Keyboard(instruments_display_frame, self.LM)
        self.guitar = displayers.Guitar(instruments_display_frame, self.LM)
        instruments_display_frame.pack()
        self.main_notebook.add(instruments_display_frame, text=self.LM.get("instruments"))

        # Accords
        chords_frame = ttk.Frame(self.main_notebook)
        self.chords = informers.Chords(chords_frame, self.LM, self.player, SCORE_WIDTH, SCORE_HEIGHT, 7)
        self.chords2 = informers.Chords(chords_frame, self.LM, self.player, SCORE_WIDTH, SCORE_HEIGHT, 7)
        chords_frame.pack()
        self.main_notebook.add(chords_frame, text=self.LM.get("chords"))

        # Scale Intersections
        scale_inter_frame = ttk.Frame(self.main_notebook)
        self.intersections = informers.IntersectionsPanel(scale_inter_frame, self.LM, self.player,
                                                          SCORE_WIDTH, SCORE_HEIGHT)
        scale_inter_frame.pack()
        self.main_notebook.add(scale_inter_frame, text=self.LM.get("intersections"))

        # Chord progression
        chord_prog_frame = ttk.Frame(self.main_notebook)
        self.chordProg = informers.Progressions(chord_prog_frame, self.LM, self.player, SCORE_WIDTH, SCORE_HEIGHT, 7)
        chord_prog_frame.pack()
        self.main_notebook.add(chord_prog_frame, text=self.LM.get("chord_progressions"))

        """
        Default Parameters
        """

        self.param_reader.set(self)
        self.__update_notes(self.selected_scale_type_SV.get())
        self.__update_usable_scales()

        """
        Menus
        """

        # init
        self.root.config(menu=self.menubar)

        # file
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label=self.LM.get("load"), command=self.__load)
        filemenu.add_command(label=self.LM.get("save"), command=self.__save)
        filemenu.add_separator()
        filemenu.add_command(label=self.LM.get("panic"), command=self.__panic)
        filemenu.add_command(label=self.LM.get("exit"), command=self.quit)
        self.menubar.add_cascade(label=self.LM.get("file"), menu=filemenu)

        # scales
        scalesmenu = tk.Menu(self.menubar, tearoff=0)
        for i in range(len(self.choosable_scales_names)):
            scalesmenu.add_checkbutton(label=self.LM.get(self.choosable_scales_names[i]), onvalue=1, offvalue=0,
                                       variable=self.chosen_scales.list_[i], command=self.__update_usable_scales)
        self.menubar.add_cascade(label=self.LM.get("scales"), menu=scalesmenu)

        # internationalization menu
        intermenu = tk.Menu(self.menubar, tearoff=0)
        langmenu = tk.Menu(intermenu, tearoff=0)
        for elem in self.LM.get_languages():
            langmenu.add_radiobutton(label=elem, variable=self.lang_SV, value=elem,
                                     command=self.__reset_root)
        convmenu = tk.Menu(intermenu, tearoff=0)
        for elem in [("french", "Do Ré Mi Fa"), ("english", "C D E F")]:
            convmenu.add_radiobutton(label=elem[1], variable=self.conv_SV, value=elem[0],
                                     command=self.__reset_root)
        intermenu.add_cascade(label=self.LM.get("note_naming"), menu=convmenu)
        intermenu.add_cascade(label=self.LM.get("text"), menu=langmenu)
        self.menubar.add_cascade(label=self.LM.get("language"), menu=intermenu)

        """
        Last Commands
        """

        self.root.title("SHIMUT")
        self.root.wm_iconbitmap("assets/main_icon.ico")
        self.root.iconbitmap("assets/main_icon.ico")
        self.root.pack_slaves()

    def __update_usable_scales(self):
        self.usable_scales = []
        groups = []
        for i in range(len(self.chosen_scales)):
            if self.chosen_scales[i].get_state() == 1:
                groups.append(self.choosable_scales_names[i])
        for group in groups:
            for scalename, scaleprop in scales.items():
                if group in scaleprop[2] and (scalename not in self.usable_scales):
                    self.usable_scales.append(scalename)
        if len(self.usable_scales) == 0:
            self.usable_scales.append("major")
        if self.selected_scale_type_SV.get_state() not in self.usable_scales:
            self.scale_chooser.set_menu(self.LM.get(self.usable_scales[0]),
                                       *[self.LM.get(e) for e in self.usable_scales])
        else:
            self.scale_chooser.set_menu(self.selected_scale_type_SV.get(),
                                       *[self.LM.get(e) for e in self.usable_scales])

    def __load(self):
        file = fd.askopenfilename(
            initialdir=str(pathlib.Path(__file__).parent.resolve())+'/parameters/',
            title=self.LM.get("load"),
            filetypes=[('SHIMUT state file', '*.SHIMUTstate')])
        if file != "":
            self.__load_parameters(file)

    def __save(self):
        file = fd.asksaveasfilename(
            initialdir=str(pathlib.Path(__file__).parent.resolve())+'/parameters/',
            title=self.LM.get("save"),
            defaultextension='.SHIMUTstate',
            filetypes=[('SHIMUT state file', '*.SHIMUTstate')])
        if file != "":
            self.param_reader.save(self, file)

    def __reset_root(self):
        self.param_reader.save(self, "parameters/temp.SHIMUTstate")
        self.__load_parameters("parameters/temp.SHIMUTstate")

    def __panic(self):
        self.__load_parameters("parameters/default.SHIMUTstate")

    def __load_parameters(self, file):
        self.quit()
        self.root.destroy()
        self.__init__(file)
        self.mainloop()

    def mainloop(self):
        self.apply()
        self.root.mainloop()

    def __update_notes(self, scaleType):
        self.usable_scale_notes = self.LM.get_notes(scales[self.LM.reverse_get(scaleType)][1])
        if self.selected_scale_note_SV.get() not in self.usable_scale_notes:
            self.note_chooser.set_menu(self.usable_scale_notes[0], *self.usable_scale_notes)
        else:
            self.note_chooser.set_menu(self.selected_scale_note_SV.get(), *self.usable_scale_notes)

    def apply(self):
        scale = [all_notes_extended[self.LM.reverse_get_note(self.selected_scale_note_SV.get())]]
        for interval in scales[self.LM.reverse_get(self.selected_scale_type_SV.get())][0]:
            scale.append((scale[-1] + interval))
        self.keyboard.apply(scale)
        self.guitar.apply(scale)
        self.chords.apply(scale)
        self.chords2.apply(scale)
        self.chordProg.apply(scale)
        self.intersections.apply(scale, self.selected_scale_note_SV.get_state(), self.usable_scales)
        self.scale = scale

    def quit(self):
        self.root.quit()
        self.player.quit()
        self.LM.quit()


"""
Main loop
"""

if __name__ == "__main__":
    main = Main()
    main.mainloop()
    main.quit()
