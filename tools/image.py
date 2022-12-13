"""
Contains all the image managing tools.
"""

from PIL import ImageTk, Image


def load_image(file_name, lx, ly):
    """
    Loads an image and makes the appropriate conversions.
    :param file_name: name of the file in the "assets" folder
    :param lx: width to resize
    :param ly: height to resize
    :return: the converted image, usable by tkinter
    """
    return ImageTk.PhotoImage(Image.open("assets/" + file_name).convert("RGBA").resize((lx, ly)))
