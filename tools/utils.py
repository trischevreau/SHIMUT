"""
Contains all the useful functions.
"""

from math import sqrt

def int_to_roman(v):
    """
    Returns the roman notation of an integer between 1 and 12
    :param v: the integer between 1 and 12
    :return: it's roman notation
    """
    assert 0 <= v <= 12 and type(v) == int
    if v == 0:
        return "0"
    elif v <= 3:
        return "I"*v
    elif v == 4:
        return "IV"
    elif v == 5:
        return "V"
    elif v <= 8:
        return "V"+"I"*(v-5)
    elif v == 9:
        return "IX"
    elif v == 10:
        return "X"
    else:
        return "X"+"I"*(v-10)


def roman_to_int(v):
    """
    Returns the int corresponding to a roman notation between 1 and 12
    :param v: the string (roman notation)
    :return: it's corresponding int
    """
    for i in range(0, 13):
        t = int_to_roman(i)
        if t == v:
            return i


def fill_spaces(s, length):
    """
    Fills with spaces to make a string to a certain length
    :param s: the string
    :param length: the length it should be
    :return: the string at the length it should be
    """
    assert len(s) <= length
    return s+" "*(length-len(s))


def un_octaver(to_scale):
    """
    Makes every note in between 0 and 11.
    :param to_scale: the scale to "un-octave"
    :return: the "un-octaved" scale
    """
    to_scale = list(to_scale)
    for i in range(len(to_scale)):
        while to_scale[i] >= 12:
            to_scale[i] -= 12
    return to_scale


def unlistify(list_):
    """
    If the list contains just one element, returns it as a single element.
    :param list_: the list to "unlistify"
    :return: the unchanged list or a single element
    """
    if len(list_) == 1:
        return list_[0]
    else:
        return list_

def euclidian_distance(v1,v2):
    """
    Calculates the euclidian distance between v1 and v2
    :param v1: the first vector
    :param v2: the second vector
    :return: the euclidian distance between them
    """
    assert len(v1)==len(v2)
    return sqrt(sum([(v1[i]-v2[i])^2 for i in range(len(v1))]))

