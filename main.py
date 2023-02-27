import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as messagebox
import tkinter.ttk as ttk
import pathlib

from varplus import StringVarPlus, BooleanDictVarPlus
from tools import managers, image
import blocks
from vars import *


class Main:

    def __init__(self, to_load="parameters/default.shimut_state"):
        """
        This creates the skeleton of the interface and the menubar.
        :param to_load: path to the shimut_state file to load.
        :return:
        """

        self.root = tk.Tk()

        # Classes init 1
        self.param_reader = managers.StateReader()
        self.param_reader.load(to_load)
        self.LM = managers.LanguageManager(self.param_reader.get("lang_SV"), self.param_reader.get("conv_SV"))

        # Variable init
        self.scale = []
        self.lang_SV = StringVarPlus(self.LM, "any")
        self.conv_SV = StringVarPlus(self.LM, "any")
        self.chosen_scales = BooleanDictVarPlus(len(sg.__dict__))
        self.available_scale_names = [e[1] for e in sg.__dict__.items()]
        self.usable_scales = []

        # Classes init 2
        self.player = managers.Player(MIDI_INSTRUMENT, MIDI_VELOCITY, MIDI_NOTE_LENGTH)
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
        self.keyboard = blocks.keyboard.Keyboard(instruments_display_frame, self.LM)
        self.guitar = blocks.guitar.Guitar(instruments_display_frame, self.LM)
        instruments_display_frame.pack()
        self.main_notebook.add(instruments_display_frame, text=self.LM.get("instruments"))

        # Transposition
        transposition_frame = ttk.Frame(self.main_notebook)
        self.chords = blocks.chords.Chords(transposition_frame, self.LM, self.player, SCORE_WIDTH, SCORE_HEIGHT, 7)
        self.chords2 = blocks.chords.Chords(transposition_frame, self.LM, self.player, SCORE_WIDTH, SCORE_HEIGHT, 7)
        transposition_frame.pack()
        self.main_notebook.add(transposition_frame, text=self.LM.get("transpose"))

        # Scale
        scale_inter_frame = ttk.Frame(self.main_notebook)
        self.intersections = blocks.intersectionsPanel.IntersectionsPanel(scale_inter_frame, self.LM, self.player,
                                                                          SCORE_WIDTH, SCORE_HEIGHT)
        scale_inter_frame.pack()
        self.main_notebook.add(scale_inter_frame, text=self.LM.get("intersections"))

        # Chord progression
        chord_prog_frame = ttk.Frame(self.main_notebook)
        self.chordProg = blocks.progressions.Progressions(
            chord_prog_frame, self.LM, self.player, SCORE_WIDTH, SCORE_HEIGHT, 7)
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
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label=self.LM.get("load"), command=self.__load)
        file_menu.add_command(label=self.LM.get("save"), command=self.__save)
        file_menu.add_separator()
        file_menu.add_command(label=self.LM.get("panic"), command=self.__panic)
        file_menu.add_command(label=self.LM.get("exit"), command=self.quit)
        self.menubar.add_cascade(label=self.LM.get("file"), menu=file_menu)

        # scales
        scales_menu = tk.Menu(self.menubar, tearoff=0)
        for i in range(len(self.available_scale_names)):
            scales_menu.add_checkbutton(label=self.LM.get(self.available_scale_names[i]), onvalue=1, offvalue=0,
                                        variable=self.chosen_scales.list_[i], command=self.__update_usable_scales)
        scales_menu.add_separator()
        scales_menu.add_command(label=self.LM.get("all"), command=self.__select_all_scales)
        scales_menu.add_command(label=self.LM.get("none"), command=self.__deselect_all_scales)
        self.menubar.add_cascade(label=self.LM.get("scales"), menu=scales_menu)

        # internationalization menu
        inter_menu = tk.Menu(self.menubar, tearoff=0)
        lang_menu = tk.Menu(inter_menu, tearoff=0)
        for elem in self.LM.get_languages():
            lang_menu.add_radiobutton(label=elem, variable=self.lang_SV, value=elem, command=self.__reset_root)
        conv_menu = tk.Menu(inter_menu, tearoff=0)
        for elem in [("french", "Do Ré Mi Fa"), ("english", "C D E F")]:
            conv_menu.add_radiobutton(label=elem[1], variable=self.conv_SV, value=elem[0], command=self.__reset_root)
        inter_menu.add_cascade(label=self.LM.get("note_naming"), menu=conv_menu)
        inter_menu.add_cascade(label=self.LM.get("text"), menu=lang_menu)
        self.menubar.add_cascade(label=self.LM.get("language"), menu=inter_menu)

        # about menu
        self.menubar.add_command(label=self.LM.get("about"), command=self.__about)

        """
        Last Commands
        """

        self.root.title("SHIMUT")
        self.root.wm_iconbitmap("assets/main_icon.ico")
        self.root.iconbitmap("assets/main_icon.ico")
        self.root.iconphoto(True, image.load_image("main_icon.ico", 16, 16))
        self.root.pack_slaves()

    def __update_usable_scales(self):
        """
        Updates the usable scales to match the ones selected by the user.
        :return:
        """
        self.usable_scales = []
        groups = []
        # list the selected groups
        for i in range(len(self.chosen_scales)):
            if self.chosen_scales[i].get_state() == 1:
                groups.append(self.available_scale_names[i])
        # extract the scales from the selected groups
        for group in groups:
            for scale_name, scale_prop in scales.items():
                if group in scale_prop[2] and (scale_name not in self.usable_scales):
                    self.usable_scales.append(scale_name)
        # if no scales where selected by the user, we leave at least one : major
        if len(self.usable_scales) == 0:
            self.usable_scales.append("major")
        # set the menu
        if self.selected_scale_type_SV.get_state() not in self.usable_scales:
            # if the selected scale isn't still available, change it to the first one
            self.scale_chooser.set_menu(self.LM.get(self.usable_scales[0]),
                                        *[self.LM.get(e) for e in self.usable_scales])
        else:
            # else, keep it
            self.scale_chooser.set_menu(self.selected_scale_type_SV.get(),
                                        *[self.LM.get(e) for e in self.usable_scales])
        self.apply()

    def __load(self):
        """
        Opens a dialog window to select a shimut_state file to load.
        :return:
        """
        file = fd.askopenfilename(
            initialdir=str(pathlib.Path(__file__).parent.resolve())+'/parameters/',
            title=self.LM.get("load"),
            filetypes=[('SHIMUT state file', '*.shimut_state')])
        if file != "":
            self.__load_parameters(file)

    def __save(self):
        """
        Opens a dialog window to choose file name to save a shimut_state file.
        :return:
        """
        file = fd.asksaveasfilename(
            initialdir=str(pathlib.Path(__file__).parent.resolve())+'/parameters/',
            title=self.LM.get("save"),
            defaultextension='.shimut_state',
            filetypes=[('SHIMUT state file', '*.shimut_state')])
        if file != "":
            self.param_reader.save(self, file)

    def __reset_root(self):
        """
        Resets the window by saving the parameters, and reloading everything.
        :return:
        """
        self.param_reader.save(self, "parameters/temp.shimut_state")
        self.__load_parameters("parameters/temp.shimut_state")

    def __about(self):
        """
        Displays an "about window".
        :return:
        """
        messagebox.showinfo(self.LM.get("about"), self.LM.get("about_text"))

    def __panic(self):
        """
        Resets everything to the default parameters.
        :return:
        """
        self.__load_parameters("parameters/default.shimut_state")

    def __load_parameters(self, file):
        """
        Loads the parameters from the state file located in the path "file".
        :param file: the path to the shimut_state file.
        :return:
        """
        self.quit()
        self.root.destroy()
        self.__init__(file)
        self.mainloop()

    def mainloop(self):
        """
        Runs the last commands and the mainloop of the root.
        :return:
        """
        self.apply()
        self.root.mainloop()

    def __update_notes(self, scale_type_):
        """
        Updates the notes available for use with the selected scale.
        :param scale_type_: the selected scale.
        :return:
        """
        self.usable_scale_notes = self.LM.get_notes(scales[self.LM.reverse_get(scale_type_)][1])
        if self.selected_scale_note_SV.get() not in self.usable_scale_notes:
            # if the previous selected note is not available anymore, change it
            self.note_chooser.set_menu(self.usable_scale_notes[0], *self.usable_scale_notes)
        else:
            self.note_chooser.set_menu(self.selected_scale_note_SV.get(), *self.usable_scale_notes)

    def __select_all_scales(self):
        """
        Selects all scales available on the menubar.
        :return:
        """
        for btn in self.chosen_scales.list_:
            btn.set_state(True)
        self.__update_usable_scales()

    def __deselect_all_scales(self):
        """
        Deselects all scales available on the menubar
        :return:
        """
        for btn in self.chosen_scales.list_:
            btn.set_state(False)
        self.__update_usable_scales()

    def apply(self):
        """
        Applies the scale, and other things, to all the blocks.
        :return:
        """
        scale_to_apply = [all_notes_extended[self.LM.reverse_get_note(self.selected_scale_note_SV.get())]]
        for delta in scales[self.LM.reverse_get(self.selected_scale_type_SV.get())][0]:
            scale_to_apply.append((scale_to_apply[-1] + delta))
        self.keyboard.apply(scale_to_apply)
        self.guitar.apply(scale_to_apply)
        self.chords.apply(scale_to_apply)
        self.chords2.apply(scale_to_apply)
        self.chordProg.apply(scale_to_apply)
        self.intersections.apply(scale_to_apply, self.selected_scale_note_SV.get_state(), self.usable_scales)
        self.scale = scale_to_apply

    def quit(self):
        """
        Exits the program cleanly.
        :return:
        """
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
