"""
Contains all the constants.
"""

from tools.utils import unoctaver

english_notation = {
    "Do": "C", "Ré": "D", "Mi": "E", "Fa": "F", "Sol": "G", "La": "A", "Si": "B",
}

all_plain_notes = {
    "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11,
}

all_notes = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11,
}

all_notes_extended = {}
for note in all_plain_notes.keys():
    all_notes_extended[str(note)] = all_plain_notes[note]
    all_notes_extended[str(note + "#")] = (all_plain_notes[note] + 1) % 12
    all_notes_extended[str(note + "x")] = (all_plain_notes[note] + 2) % 12
    all_notes_extended[str(note + "b")] = (all_plain_notes[note] - 1) % 12
    all_notes_extended[str(note + "bb")] = (all_plain_notes[note] - 2) % 12

circle = {
    "M": ["C", "G", "D", "A", "E", "B", "F#", "C#", "F", "Bb", "Eb", "A#", "Db", "Gb", "Cb"],
    "m": ["A", "E", "B", "F#", "C#", "G#", "D#", "A#", "D", "G", "C", "F", "Bb", "Eb", "Ab"],
}


class scale_groups:
    def __init__(self):
        self.CLASSIC = "classic"
        self.DIATONIC = "diatonic"
        self.PENTATONIC = "pentatonic"
        self.HEXATONIC = "hexatonic"
        self.FROM_MEL_MINOR = "from_melodic_minor"
        self.FROM_HARM_MINOR = "from_harmonic_minor"


sg = scale_groups()


scales = {
    # From major
    "major": ([2, 2, 1, 2, 2, 2], circle["M"], [sg.DIATONIC, sg.CLASSIC]),
    "dorian": ([2, 1, 2, 2, 2, 1], list(all_notes.keys()), [sg.DIATONIC]),
    "phrygian": ([1, 2, 2, 2, 1, 2], list(all_notes.keys()), [sg.DIATONIC]),
    "lydian": ([2, 2, 2, 1, 2, 2], list(all_notes.keys()), [sg.DIATONIC]),
    "mixolydian": ([2, 2, 1, 2, 2, 1], list(all_notes.keys()), [sg.DIATONIC]),
    "locrian": ([1, 2, 2, 1, 2, 2], list(all_notes.keys()), [sg.DIATONIC]),
    "natural_minor": ([2, 1, 2, 2, 1, 2], circle["m"], [sg.DIATONIC, sg.CLASSIC]),
    # special
    "whole_tone": ([2, 2, 2, 2, 2], list(all_notes.keys()), [sg.HEXATONIC]),
    "pentatonic_major": ([2, 2, 3, 2], list(all_notes.keys()), [sg.PENTATONIC]),
    "pentatonic_minor": ([3, 2, 2, 3], list(all_notes.keys()), [sg.PENTATONIC]),
    # From melodic minor
    "melodic_minor": ([2, 1, 2, 2, 2, 2], circle["m"], [sg.FROM_MEL_MINOR, sg.CLASSIC]),
    "javanese": ([1, 2, 2, 2, 2, 1], list(all_notes.keys()), [sg.FROM_MEL_MINOR]),
    "augmented_lydian": ([2, 2, 2, 2, 1, 2], list(all_notes.keys()), [sg.FROM_MEL_MINOR]),
    "bartok": ([2, 2, 2, 1, 2, 1], list(all_notes.keys()), [sg.FROM_MEL_MINOR]),
    "hindu": ([2, 2, 1, 2, 1, 2], list(all_notes.keys()), [sg.FROM_MEL_MINOR]),
    "diminished_minor": ([2, 1, 2, 1, 2, 2], list(all_notes.keys()), [sg.FROM_MEL_MINOR]),
    "altered_minor": ([1, 2, 1, 2, 2, 2], list(all_notes.keys()), [sg.FROM_MEL_MINOR]),
    # From harmonic minor
    "harmonic_minor": ([2, 1, 2, 2, 1, 3], circle["m"], [sg.CLASSIC, sg.FROM_HARM_MINOR]),
    "locrian_6M": ([1, 2, 2, 1, 3, 1], list(all_notes.keys()), [sg.FROM_HARM_MINOR]),
    "augmented_minor": ([2, 2, 1, 3, 1, 2], list(all_notes.keys()), [sg.FROM_HARM_MINOR]),
    "romanian": ([2, 1, 3, 1, 2, 1], list(all_notes.keys()), [sg.FROM_HARM_MINOR]),
    "spanish_phrygian": ([1, 3, 1, 2, 1, 2], list(all_notes.keys()), [sg.FROM_HARM_MINOR]),
    "lydian_9#": ([3, 1, 2, 1, 2, 2], list(all_notes.keys()), [sg.FROM_HARM_MINOR]),
    "altered_minor_7dim": ([1, 2, 1, 2, 2, 1], list(all_notes.keys()), [sg.FROM_HARM_MINOR]),
}

progressions = {
    "perfect_cadence": ["V", "I"],
    "imperfect_cadence_V": ["V/", "I"],
    "imperfect_cadence_I": ["V", "I/"],
    "plagal_cadence_IV": ["IV", "I"],
    "plagal_cadence_II": ["II", "I"],
    "plagal_cadence_VI": ["VI", "I"],
    "deceptive_cadence": ["V", "VI"]
}

universe = []  # item : (Type, Note, Scale)
for scale_type in scales.keys():
    for note in scales[scale_type][1]:
        temp = [all_notes_extended[note]]
        for interval in scales[scale_type][0]:
            temp.append(temp[-1] + interval)
        universe.append([scale_type, note, temp])

relatives = {}  # key : sorted scale, item : (Type, Note)
for scale in universe:
    scale[2] = unoctaver(scale[2])
    if tuple(scale[2]) not in list(relatives.keys()):
        relatives[tuple(scale[2])] = [(scale[0], scale[1])]
    else:
        relatives[tuple(scale[2])].append((scale[0], scale[1]))

try:
    del scale, temp, scale_type
except NameError:
    pass

colors_full = ['snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
               'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
               'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
               'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
               'light slate gray', 'gray', 'light gray', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
               'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue', 'blue',
               'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
               'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
               'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
               'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
               'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
               'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
               'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
               'indian red', 'saddle brown', 'sandy brown',
               'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
               'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
               'pale violet red', 'maroon', 'medium violet red', 'violet red',
               'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
               'thistle']

colors = ['snow', 'linen', 'azure', 'lavender blush', 'light slate gray', 'slate blue', 'dodger blue', 'light blue',
          'cyan', 'dark sea green', 'lawn green', 'forest green', 'yellow', 'indian red', 'dark salmon', 'coral',
          'pale violet red', 'medium orchid', 'thistle']

GUITAR_LENGTH = 21

GUITAR_DOTS = [(3, "*"), (5, "*"), (7, "*"), (9, "*"), (12, "**"), (15, "*"), (17, "*"), (19, "*")]

SCORE_WIDTH = 600
SCORE_HEIGHT = 200

MIDI_INSTRUMENT = 0
MIDI_VELOCITY = 127
MIDI_NOTE_LENGTH = 0.2
