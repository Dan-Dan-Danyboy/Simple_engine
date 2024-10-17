from graficos_tabla import *
from interfaz_user import *
from tkinter import ttk

# Function that is called when a button is pressed
game_mode = None
def button_pressed(option):
    global game_mode
    root.destroy()  # Close the window after button is pressed
    game_mode = option

# Create the main window
root = tk.Tk()
root.title("Sheep vs Wolf")

# Set window size and remove default maximize/minimize buttons for simplicity
root.geometry("400x300")
root.resizable(False, False)

# Use ttk style for modern buttons
style = ttk.Style()
style.theme_use('clam')  # Use a clean theme
style.configure("TButton",
                font=('Helvetica', 14),
                padding=10,
                relief="flat",
                background='#4CAF50',  # Background for buttons
                foreground='#ffffff',  # White text color
                focuscolor='none',  # Remove focus border
                borderwidth=0)
style.map("TButton",
          background=[('active', '#45a049'), ('!active', '#4CAF50')])  # Button color on hover

# Frame for centering widgets and adding padding
frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
frame.pack(expand=True)

# Add a title label for more modern look
title_label = tk.Label(frame, text="CHOOSE GAMEMODE", font=("Helvetica", 18, 'bold'), bg='#f0f0f0')
title_label.pack(pady=10)

# Modern Buttons using ttk
button1 = ttk.Button(frame, text="1v1 player", command=lambda: button_pressed("1v1 player"))
button2 = ttk.Button(frame, text="Human (sheep) vs Computer (wolf)", command=lambda: button_pressed("Human (sheep) vs Computer (wolf)"))
button3 = ttk.Button(frame, text="Human (wolf) vs Computer (sheep)", command=lambda: button_pressed("Human (wolf) vs Computer (sheep)"))

# Pack buttons with equal spacing for modern layout
button1.pack(fill='x', pady=10)
button2.pack(fill='x', pady=10)
button3.pack(fill='x', pady=10)

# Start the Tkinter event loop
root.mainloop()

# Create an 8x8 chessboard with coordinates and each square of size 60x60 pixels
create_chessboard_with_coordinates(8, 60,game_mode)
