"""
This contains the managing tools for the software.
"""

import sqlite3
from tools import converters
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import pygame.midi as midi
from time import sleep
from midiutil.MidiFile import MIDIFile


class LanguageManager:
    """ This class is meant to be shared among the script to get the text efficiently """

    def __init__(self, lang="EN", note_notation="english"):
        """
        Opens the database and prepares variables
        :param lang: the language in use for this run
        :param note_notation: the note notation used throughout the classes
        """
        self.lang = lang
        self.note_notation = note_notation
        self.bdd = sqlite3.connect("data/languages.db")
        self.cur = self.bdd.cursor()
        self.texts = {}

    def reverse_get(self, text_to_find):
        """
        Returns the text_name associated with a text that's in buffer memory
        :param text_to_find: the text to find the text_name of
        :return: the text_name, if found
        """
        for text_name, text in self.texts.items():
            if text == text_to_find:
                return text_name
        # no corresponding text was found
        print("Warn : Missing associated text_name for text <", text_to_find, ">")
        return None

    def get(self, text_name):
        """
        Returns the text efficiently by keeping a buffer of already used words
        :param text_name: the name of the text that needs to be extracted
        :return: the extracted name
        """
        try:
            return self.texts[text_name]
        except KeyError:  # if the text is not already in memory ...
            # ... try getting it from the database
            r = self.cur.execute("SELECT " + self.lang + " FROM texts WHERE text_name == '" + text_name + "'").fetchone()
            if r is not None:
                self.texts[text_name] = r[0]
                return r[0]
            else:  # if the database was empty ...
                # ... warn the user
                print("Warn : Missing text_name entry <", text_name, ">")
                return "!! ERROR !!"

    def get_note(self, note):
        """
        Returns the display name of a note
        :param note: the note (internal notation : English)
        :return: the display name of the note (English or French)
        """
        if self.note_notation == "french":
            return converters.convert_english_to_french(note)
        else:
            return note

    def reverse_get_note(self, note):
        """
        Return the note's internal notation (English) using its display name
        :param note: the display name of this note
        :return: the internal notation of this note
        """
        if self.note_notation == "french":
            return converters.convert_french_to_english(note)
        else:
            return note

    def get_notes(self, notes):
        """ the same as get_note but for iterables """
        return [self.get_note(note) for note in notes]

    def reverse_get_notes(self, notes):
        """ the same as reverse_get_note but for iterables """
        return [self.reverse_get_note(note) for note in notes]

    def quit(self):
        """ quits cleanly the database to avoid conflicts """
        self.cur.close()

    def get_languages(self):
        """ returns the list of supported languages """
        data = self.cur.execute('SELECT * FROM texts')
        r = []
        for column in data.description:
            r.append(column[0])
        return r[1:]


class Player:
    """
    This class uses pygame to play sound (using the midi instrument emulator)
    """

    def __init__(self, instrument, velocity, length):
        """
        Initializes the class
        :param instrument: the selected midi instrument
        :param velocity: the velocity of each note that will be played
        :param length: the length of each note that will be played and the silence in between a series
        """
        midi.init()
        self.midi_out = midi.Output(midi.get_default_output_id(), 0)
        self.midi_out.set_instrument(instrument)
        self.velocity = velocity
        self.length = length

    def play_note(self, notes_list):
        """
        Plays the notes
        :param notes_list: the notes to play. Example : [[chordnote1,chordnote2],[othernote1],...]
        """
        length = len(notes_list)
        for notes_index in range(length):
            notes = notes_list[notes_index]
            for n in notes:
                self.midi_out.note_on(50+n, self.velocity)
            sleep(self.length)
            for n in notes:
                self.midi_out.note_off(50+n, self.velocity)
            if notes_index+1!=length:
                sleep(self.length)

    def quit(self):
        """ Destroys cleanly the class and midi instruments to avoid causing interferences. """
        midi.quit()


class StateReader:

    """ This class reads states from files to apply it to every instance contained in the main class. """

    def __init__(self):
        self.file_path = None
        self.dict_ = None

    def load(self, file_path):
        """
        Loads the states from a shimut_state file
        :param file_path: the path of the shimut_state file
        :return:
        """
        self.file_path = file_path
        self.dict_ = {}
        with open(self.file_path, "r") as file:
            for line in file.readlines():
                line = line.rstrip().split(";")
                if len(line[1:]) == 1:
                    self.dict_[line[0]] = line[1:][0]
                else:
                    self.dict_[line[0]] = line[1:]
        return self.dict_

    def get(self, name):
        """
        Returns the state for a specific name.
        :param name: the name of the instance
        :return: the state
        """
        if self.file_path is not None:
            return self.dict_[name]
        else:
            raise ValueError

    def set(self, to_set):
        """
        Sets the states of an instance
        :param to_set: the class to run through
        :return:
        """
        for key, val in to_set.__dict__.items():
            try:
                val.set_state(self.dict_[key])
            except AttributeError:
                pass

    def save(self, to_save, file_path):
        """
        Saves the parameters from an instance to a shimut_state file.
        :param to_save: instance that needs to be saved
        :param file_path: the path to save it to
        :return:
        """
        states = {}
        for key, val in to_save.__dict__.items():
            try:
                states[key] = val.get_state()
            except AttributeError:
                pass
        with open(file_path, "w") as file:
            for key, val in states.items():
                if type(val) not in [list, tuple]:
                    file.write(key+";"+val+"\n")
                else:
                    val = [str(v) for v in val]
                    file.write(key+";"+";".join(val)+"\n")

class MIDIFileWriter:

    """ This class manages MIDI files. """

    def __init__(self, LM):
        self.mf = MIDIFile(1)  # only 1 track
        self.track = 0  # the only track
        self.time = 0
        self.mf.addTrackName(self.track, self.time, "Track")
        self.mf.addTempo(self.track, self.time, 120)
        self.channel = 0
        self.volume = 100
        self.LM = LM

    def add_notes(self, length, pitch_list):
        for pitch in pitch_list:
            self.mf.addNote(self.track, self.channel, pitch, self.time, length, self.volume)
        self.time += length

    def add_note(self, length, pitch):
        self.mf.addNote(self.track, self.channel, pitch, self.time, length, self.volume)
        self.time += length

    def write_file(self, path=None):
        if path is None:
            path = fd.asksaveasfilename(
                title=self.LM.get("save"),
                defaultextension=".mid",
                filetypes=[('MIDI file', '*.mid')])
        if path != "":
            with open(path, 'wb') as outf:
                self.mf.writeFile(outf)


def give_help(subject, LM):

    # initialize the help database
    lang = LM.lang
    bdd = sqlite3.connect("data/help.db")
    cur = bdd.cursor()

    # try getting the selected langage from the database
    r = cur.execute("SELECT " + lang + " FROM texts WHERE subject == '" + subject + "'").fetchone()
    if r is not None:
        text = r[0]
    else:  # if there was no entry for this langage
        print("Warn : Missing text_name entry <", subject, "> for langage <", lang, ">")
        return None

    # display the text
    showinfo(LM.get("help"), text)

    # end routine
    cur.close()
