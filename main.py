import tkinter as tk
from tkinter import filedialog as fd
from random import choice
import tkinter.ttk as ttk
import os
import pathlib

from VarPlus import StringVarPlus

import managers
import displayers
import informers
from managers import ParamReader
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
        self.param_reader = ParamReader()
        self.param_reader.load(to_load)
        self.LM = managers.LanguageManager(self.param_reader.get("lang_SV"), self.param_reader.get("conv_SV"))

        # Variable init
        self.scale = []
        self.lang_SV = StringVarPlus(self.LM, "any")
        self.conv_SV = StringVarPlus(self.LM, "any")

        # Classes init 2
        self.player = managers.Player(0, 127, 0.2)
        self.menubar = tk.Menu(self.root)
        self.mainNotebook = ttk.Notebook(self.root)

        """
        Scale parameters
        """

        # Parameter frames
        self.parametersFrame = ttk.Frame(self.root)
        self.scaleParametersFrame = ttk.LabelFrame(self.parametersFrame, text=self.LM.get("scale_parameters"),
                                                   name="params")
        # Scale Type
        self.selectedScaleTypeSV = StringVarPlus(self.LM, "text_db")
        self.scaleChooser = ttk.OptionMenu(self.scaleParametersFrame, self.selectedScaleTypeSV, None,
                                           *[self.LM.get(elem) for elem in scales.keys()], command=self.update_notes)
        self.scaleChooser.pack(side="right")

        # Scale height
        self.usableScaleNotes = []
        self.selectedScaleNoteSV = StringVarPlus(self.LM, "note")
        self.noteChooser = ttk.OptionMenu(self.scaleParametersFrame, self.selectedScaleNoteSV, None)
        self.noteChooser["menu"].delete(0, "end")
        self.noteChooser.pack(side="left")

        self.scaleParametersFrame.grid(row=0, column=0)

        """
        Display Parameters
        """

        self.displayParametersFrame = ttk.LabelFrame(self.parametersFrame, text=self.LM.get("display_parameters"))
        self.displayParametersFrame.grid(row=0, column=1)

        """
        Apply Button
        """

        self.ApplyButton = ttk.Button(self.parametersFrame, text=self.LM.get("apply"), command=self.apply)
        self.ApplyButton.grid(row=0, column=3)

        self.parametersFrame.pack()

        """
        Notebook Display
        """

        self.mainNotebook.pack(expand=True)

        # Display of instruments
        self.instrumentsDisplayFrame = ttk.Frame(self.mainNotebook)
        self.keyboard = displayers.Keyboard(self.instrumentsDisplayFrame, self.LM)
        self.guitar = displayers.Guitar(self.instrumentsDisplayFrame, self.LM)
        self.instrumentsDisplayFrame.pack()
        self.mainNotebook.add(self.instrumentsDisplayFrame, text=self.LM.get("instruments"))

        # Accords
        self.chordsFrame = ttk.Frame(self.mainNotebook)
        self.chords = informers.Chords(self.chordsFrame, self.LM, self.player, 600, 200, 7)
        self.chords2 = informers.Chords(self.chordsFrame, self.LM, self.player, 600, 200, 7)
        self.chordsFrame.pack()
        self.mainNotebook.add(self.chordsFrame, text=self.LM.get("chords"))

        # Scale Info
        self.scaleInfoFrame = ttk.Frame(self.mainNotebook)
        self.relatives = informers.RelativeScales(self.scaleInfoFrame, self.LM)
        self.scaleInfoFrame.pack()
        self.mainNotebook.add(self.scaleInfoFrame, text=self.LM.get("info"))

        # Chord progression
        self.chordProgFrame = ttk.Frame(self.mainNotebook)
        self.chordProg = informers.Progressions(self.chordProgFrame, self.LM, self.player, 600, 200, 7)
        self.chordProgFrame.pack()
        self.mainNotebook.add(self.chordProgFrame, text=self.LM.get("chord_progressions"))

        """
        Default Parameters
        """

        self.param_reader.set(self)
        self.update_notes(self.selectedScaleTypeSV.get())

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

    def update_notes(self, scaleType):
        self.usableScaleNotes = self.LM.get_notes(scales[self.LM.reverse_get(scaleType)][1])
        if self.selectedScaleNoteSV.get() not in self.usableScaleNotes:
            self.noteChooser.set_menu(self.usableScaleNotes[0], *self.usableScaleNotes)
        else:
            self.noteChooser.set_menu(self.selectedScaleNoteSV.get(), *self.usableScaleNotes)

    def apply(self):
        scale = [all_notes_extended[self.LM.reverse_get_note(self.selectedScaleNoteSV.get())]]
        for interval in scales[self.LM.reverse_get(self.selectedScaleTypeSV.get())][0]:
            scale.append((scale[-1] + interval))
        self.keyboard.apply(scale)
        self.guitar.apply(scale)
        self.relatives.apply(scale)
        self.chords.apply(scale)
        self.chords2.apply(scale)
        self.chordProg.apply(scale)
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
