import tkinter as tk
from random import choice
import tkinter.ttk as ttk

import managers
import displayers
import informers
from vars import *
from utils import *


class Main:

    def __init__(self, lang="EN", conv="english"):
        """
        This creates the skeleton of the interface
        :param lang: the language of the software
        :param conv: the notation to use to display the notes
        """

        self.root = tk.Tk()

        # Variable init
        self.scale = []
        self.lang_SV = tk.StringVar()
        self.conv_SV = tk.StringVar()
        self.lang_SV.set(lang)
        self.conv_SV.set(conv)

        # Classes init
        self.player = managers.Player(0, 127, 0.2)
        self.menubar = tk.Menu(self.root)
        self.LM = managers.LanguageManager(self.lang_SV.get(), self.conv_SV.get())
        self.mainNotebook = ttk.Notebook(self.root)

        """
        Scale parameters
        """

        # Parameter frames
        self.parametersFrame = ttk.Frame(self.root)
        self.scaleParametersFrame = ttk.LabelFrame(self.parametersFrame, text=self.LM.get("scale_parameters"),
                                                   name="params")
        # Scale Type
        self.selectedScaleTypeSV = tk.StringVar()
        self.scaleChooser = ttk.OptionMenu(self.scaleParametersFrame, self.selectedScaleTypeSV, None,
                                           *[self.LM.get(elem) for elem in scales.keys()], command=self.update_notes)
        self.scaleChooser.pack(side="right")

        # Scale height
        self.usableScaleNotes = []
        self.selectedScaleNoteSV = tk.StringVar()
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

        self.selectedScaleTypeSV.set(choice([self.scaleChooser['menu'].entrycget(i, "label")
                                             for i in range(self.scaleChooser['menu'].index("end") + 1)]))
        self.update_notes(self.selectedScaleTypeSV.get())
        self.selectedScaleNoteSV.set(choice([self.noteChooser['menu'].entrycget(i, "label")
                                             for i in range(self.noteChooser['menu'].index("end") + 1)]))

        """
        Menus
        """

        # init
        self.root.config(menu=self.menubar)
        # file
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label=self.LM.get("load"), command=self.load)
        filemenu.add_command(label=self.LM.get("save"), command=self.save)
        filemenu.add_separator()
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

    def __reset_root(self):
        self.quit()
        self.root.destroy()
        self.__init__(self.lang_SV.get(), self.conv_SV.get())
        self.mainloop()

    def mainloop(self):
        self.apply()
        self.root.mainloop()

    def update_notes(self, scaleType):
        self.usableScaleNotes = self.LM.get_notes(scales[self.LM.reverse_get(scaleType)][1])
        self.noteChooser.set_menu(self.usableScaleNotes[0], *self.usableScaleNotes)

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

    def load(self, *args):
        pass

    def save(self, *args):
        pass


"""
Main loop
"""

if __name__ == "__main__":
    main = Main("FR", "french")
    main.mainloop()
    main.quit()
