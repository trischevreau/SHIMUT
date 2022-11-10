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
        if k in note:
            return note.replace(k, v)


def convert_english_to_french(note):
    """
    Converts the english notation to the French one
    :param note: "C", "Dx", "Eb", "D#dim" for example
    :return: "Do", "Réx", "Mib", "Ré#dim" for example
    """
    h = note[0]  # the letter corresponding to the note
    alt = note[1:]  # this is an empty string if the note is plain
    for k, v in english_notation.items():  # reverse search in the dictionary
        if v == h:
            if len(alt) != 0:
                return str(k + alt)
            else:
                return str(k)


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
