"""
This file contains the converters for these notations :
- Do Re Mi ... French
- C D E ... English
- 0 2 4 ... SHIMUTs' own notation (easier to manage intervals and C# - Db are noted the exact same), called height
Some converters would be useless, so they are not implemented.
"""

from vars import english_notation, all_notes


def convert_french_to_english(note):
    """
    Converts the French notation to the english one
    :param note: "Do", "Réx", "Mib" for example
    :return: "C", "Dx", "Eb" for example
    """
    for k, v in english_notation.items():
        while k in note:
            note = note.replace(k, v)
    return note


def convert_english_to_french(note):
    """
    Converts the english notation to the French one
    :param note: "C", "Dx", "Eb", "D#dim" for example
    :return: "Do", "Réx", "Mib", "Ré#dim" for example
    """
    replace_list = []
    for k, v in english_notation.items():  # reverse search in the dictionary
        for i in range(len(note)):
            if note[i] == v:
                replace_list.append((i, k))
    delta = 0
    replace_list.sort(key=lambda v: v[0])
    replace_list.reverse()
    for item in replace_list:
        note = note[0:item[0]] + item[1] + note[item[0]+1:]
    return note


def convert_height_to_english(h):
    """
    Converts the height notation to the English one
    :param h: 0, 3, 5 for example
    :return: "C", "D #", "F" for example
    """
    h = h % 12  # all_notes uses a scale of 0-11 for height notation
    for k, v in all_notes.items():  # reverse search in all_notes
        if v == h:
            return k


def convert_height_to_french(h):
    """
    Converts the height notation to the French one, using the other converters.
    :param h:  0, 3, 5 for example
    :return: "Do", "Ré#", "Fa"
    """
    return convert_english_to_french(convert_height_to_english(h))

def convert_height_to_midi(h, starting=60):
    """
    Converts the height notation to a MIDI height.
    :param h:  0, 3, 5 for example
    :param starting: the starting note, C4 by default
    :return: with default starting note (C4) : 60, 63, 65
    """
    return h+starting

