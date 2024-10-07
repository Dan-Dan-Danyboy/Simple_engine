def coordinate_converter(row, column):
    """Converts row and column numbers to coordinates in the specified system.

    Args:
    row: The row number (0-7).
    column: The column number (0-7).

    Returns:
    The coordinates in the specified system (e.g., 'A8').
    """
    columns = ['A','B','C','D','E','F','G','H']
    # Convert column number to a letter
    column_letter = columns[column]

    # Calculate row number (reverse order)
    row_number = 8 - row

    # Convert row and column numbers to coordinates
    coordinates = column_letter + str(row_number)

    return str(coordinates)

# Function to convert chess notation (e.g., B6) to row and column indices
def chess_notation_to_index(notation):
    col = ord(notation[0].lower()) - ord('a')  # Convert letter to column index
    row = 8 - int(notation[1])  # Convert number to row index
    return row, col

import tkinter as tk
from tkinter import messagebox

def freeze_and_show_message(message, root):
    # Create a new top-level window (popup)
    popup = tk.Toplevel(root)
    popup.title("Message")

    # Freeze the main window
    popup.transient(root)  # Set to be on top of the main window
    popup.grab_set()  # Disable interaction with other windows
    
    # Set the size and layout of the popup
    popup.geometry("300x150")
    popup.resizable(False, False)

    # Create a label to display the message
    label = tk.Label(popup, text=message, font=("Arial", 12), padx=20, pady=20)
    label.pack(pady=10)

    # Add an OK button to close the popup
    def close_popup():
        popup.destroy()  # Destroy the popup window, re-enabling the main window

    ok_button = tk.Button(popup, text="OK", command=close_popup)
    ok_button.pack(pady=10)

    # This line makes the popup modal and freezes the main window until it is closed
    popup.wait_window(popup)

def show_message_on_current_screen(root, message):
    # Create a transparent overlay frame that covers the entire window
    overlay = tk.Frame(root, bg='gray', opacity=0.5)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Create a message frame in the center
    message_frame = tk.Frame(overlay, bg="white", bd=5)
    message_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=150)

    # Display the message label
    label = tk.Label(message_frame, text=message, font=("Arial", 12))
    label.pack(pady=20)

    # Add an OK button to close the message overlay
    def close_overlay():
        overlay.destroy()

    ok_button = tk.Button(message_frame, text="OK", command=close_overlay)
    ok_button.pack()

def diagonals_below(notation):
    # Convert input chess notation to row and column indices
    row, col = chess_notation_to_index(notation)

    diagonals = []
    
    # Calculate lower-left diagonal (row - 1, col - 1)
    if row + 1 < 8 and col - 1 >= 0:
        diagonals.append(coordinate_converter(row + 1, col - 1))

    # Calculate lower-right diagonal (row - 1, col + 1)
    if row + 1 < 8 and col + 1 < 8:
        diagonals.append(coordinate_converter(row + 1, col + 1))

    return diagonals

def unprotected(notation,squares):
    for diagonal_below in diagonals_below(notation):
        if diagonal_below in squares:
            return False
    return True