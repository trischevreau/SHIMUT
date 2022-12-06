from PIL import ImageTk, Image


def load_image(file_name, lx, ly, root=None):
    return ImageTk.PhotoImage(Image.open("assets/" + file_name).convert("RGBA").resize((lx, ly)))
