import tkinter as tk
from PIL import Image, ImageTk
import os

# Load the image using Pillow
path_to_wolf_image = os.path.join("graficas piezas","wolf.png")
path_to_sheep_image = os.path.join("graficas piezas","sheep.png")
main_path = r"C:\Users\34673\Documents\Python\chess"

def wolf(square_size,main_path):
    global tk_img_wolf
    img = Image.open(os.path.join(main_path,path_to_wolf_image))
    img = img.resize((square_size - 20, square_size - 20))  # Adjusting the image size with some margin
    tk_img = ImageTk.PhotoImage(img)
    return tk_img_wolf

def sheep(square_size,main_path):
    global tk_img_sheep
    img = Image.open(os.path.join(main_path,path_to_sheep_image))
    img = img.resize((square_size - 20, square_size - 20))  # Adjusting the image size with some margin
    tk_img = ImageTk.PhotoImage(img)
    return tk_img_sheep

tk_img_wolf = wolf(200,main_path)
tk_img_sheep = sheep(200,main_path)

# # Create the main window
# root = tk.Tk()
# root.title("Image in Tkinter")

# # img = Image.open(os.path.join(main_path,path_to_sheep_image))
# # img = img.resize((200,200))  # Adjusting the image size with some margin
# # tk_img = ImageTk.PhotoImage(img)

# # Create a label to hold the image
# label = tk.Label(root, image=wolf(200,main_path))
# label.pack()

# # Run the application
# root.mainloop()
