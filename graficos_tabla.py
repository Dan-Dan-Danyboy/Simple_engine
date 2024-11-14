import tkinter as tk
from interfaz_user import *
from tkinter import PhotoImage
import os
# from engine import output_best_move
import time
import subprocess

engine = os.path.join(os.getcwd(),"Engine_c.exe")
wolf_image = os.path.join(os.getcwd(),'graficas piezas','lobo_transparente.png')
sheep_image = os.path.join(os.getcwd(),'graficas piezas','sheep_transparente.png')

def add_circle(canvas, notation, square_size, circles, image_path=wolf_image):
    row, col = chess_notation_to_index(notation)
    
    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Set the margin and calculate the scaling factor for subsampling
    margin = 10  # Margin inside the square
    scaling_factor = 4  # Adjust this factor to make the image smaller (must be an integer)
    
    # Load the image and make it smaller using subsample
    img = PhotoImage(file=image_path)
    img = img.subsample(scaling_factor, scaling_factor)  # Reduce the image size
    
    # Calculate the center coordinates for the image
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    # Create the image on the canvas
    canvas.create_image(center_x, center_y, image=img)

    # Store the notation of the square that contains an image
    circles.add(notation)

    # Keep a reference to the image to prevent garbage collection
    canvas.image = img

def draw_light_red_circle(canvas, notation, square_size):
    # Calculate the top-left and bottom-right coordinates of the square
    row, col = chess_notation_to_index(notation)
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Calculate the coordinates for the circle (to fit inside the square)
    margin = 10  # Margin inside the square
    return canvas.create_oval(x1 + margin, y1 + margin, x2 - margin, y2 - margin, outline='red', width=2)

def add_square(canvas, notation, square_size, squares):
    row, col = chess_notation_to_index(notation)
    
    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Calculate the coordinates for the circle (to fit inside the square)
    margin = 10  # Margin inside the square
    canvas.create_rectangle(x1 + margin, y1 + margin, x2 - margin, y2 - margin, fill='green')

    # Store the notation of the square that contains a circle
    squares.add(notation)

def add_square(canvas, notation, square_size, squares, images_list = [], image_path=sheep_image):
    row, col = chess_notation_to_index(notation)
    
    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Set the margin and calculate the scaling factor for subsampling
    margin = 10  # Margin inside the square
    scaling_factor = 8  # Adjust the scaling factor to make the image smaller
    
    # Load the image and make it smaller using subsample
    img = PhotoImage(file=image_path)
    img = img.subsample(scaling_factor, scaling_factor)  # Reduce the image size
    
    # Calculate the center coordinates for the image (within the margins)
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    # Create the image on the canvas
    canvas.create_image(center_x, center_y, image=img)

    # Store the notation of the square that contains an image
    squares.add(notation)

    # Keep a reference to the image to prevent garbage collection by storing it in a list
    images_list.append(img)

def delete_all_circles(canvas, square_size, circles):
    # Loop through each chess notation in the circles set
    for notation in list(circles):  # Create a list from the set to avoid modifying it while iterating
        row, col = chess_notation_to_index(notation)

        # Calculate the top-left and bottom-right coordinates of the square
        x1 = col * square_size + 20
        y1 = row * square_size + 20
        x2 = x1 + square_size
        y2 = y1 + square_size

        # Find and delete all items enclosed within the square
        enclosed_items = canvas.find_enclosed(x1, y1, x2, y2)
        for item in enclosed_items:
            canvas.delete(item)  # Delete all items (circle and other elements if any) in the square

    # Clear the circles set since all circles have been deleted
    circles.clear()

def delete_square_by_coordinate(canvas, notation, square_size):
    # Convert chess notation (e.g., "B6") to row and column indices
    row, col = chess_notation_to_index(notation)

    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20  # 20 is the margin offset we used for the board
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size

    # Find all items (including the square) that are enclosed within the square area
    enclosed_items = canvas.find_enclosed(x1, y1, x2, y2)

    # Delete all items (including the square) found within this area
    for item in enclosed_items:
        canvas.delete(item)

def add_circle_on_click(event, canvas, square_size, circles):
    # Get the row and column from the clicked position
    col = (event.x - 20) // square_size
    row = (event.y - 20) // square_size
    
    # Check if the click is within the chessboard boundaries
    if 0 <= row < 8 and 0 <= col < 8:
        # Convert the row and column to chess notation
        notation = coordinate_converter(row, col)
        # If the square doesn't already have a circle, add one
        if notation not in circles:
            add_circle(canvas, notation, square_size, circles)

# List to store the IDs of all light gray circles
light_circles,previous_light_circles_notations, light_red_circles = [],[],[]
light_squares,previous_light_squares_notations, notation_to_delete, light_red_squares = [],[],[],[]
ready_to_move,pawn_to_move = [False],[False]

# Function to erase all the light gray circles
def erase_light_circles(canvas):
    global light_circles, light_red_circles
    for circle_id in light_circles:
        canvas.delete(circle_id)  # Remove each circle from the canvas
    light_circles.clear()  # Clear the list after deletion
    for circle_id in light_red_circles:
        canvas.delete(circle_id)  # Remove each circle from the canvas
    light_red_circles.clear()  # Clear the list after deletion

def erase_light_squares(canvas):
    global light_squares, light_red_squares
    for square_id in light_squares:
        canvas.delete(square_id)  # Remove each circle from the canvas
    light_squares.clear()  # Clear the list after deletion
    for square_id in light_red_squares:
        canvas.delete(square_id)  # Remove each circle from the canvas
    light_squares.clear()  # Clear the list after deletion

def highlight_row_column_on_click(event, canvas, square_size, circles, squares, gamemode):
    global light_circles
    global light_squares
    global light_red_circles
    global light_red_squares

    # Get the row and column from the clicked position
    col = (event.x - 20) // square_size
    row = (event.y - 20) // square_size
    notation = coordinate_converter(row,col)

    # Erase previous light gray circles
    erase_light_circles(canvas)
    erase_light_squares(canvas)

    if gamemode == "Human (wolf) vs Computer (sheep)" and pawn_to_move[-1]:
        print('processing...')
        t1 = time.time()
        if len(squares)==8 or len(squares)==7:
            depth = 8
        elif len(squares)>4:
            depth = 10
        elif len(squares)>3:
            depth = 11
        else:
            depth = 12
        # pc_move = output_best_move([list(squares),list(circles)],pawn_to_move[-1],depth)[0]
        with open("sheep.txt","w") as file:
            file.write(str(list(squares)))
        with open("wolf.txt","w") as file:
            file.write(str(list(circles)))
        subprocess.run([engine,str(1),str(depth)])
        pc_move = binary_to_cardesian()[0]
        add_square(canvas,find_difference(list(squares),pc_move),square_size,squares)
        pawn_to_move.append(False)
        delete_square_by_coordinate(canvas,find_difference(pc_move,list(squares)),square_size)
        squares.remove(find_difference(pc_move,list(squares)))
        light_squares.clear()
        previous_light_squares_notations.clear()
        if not find_difference(list(squares),pc_move) == None:
            if find_difference(list(squares),pc_move)[1] == '8':
                root = tk.Tk()  # This is the main Tkinter window
                # root.geometry("600x400")
                freeze_and_show_message('Sheeps win!',root)
        print(f'Time: {time.time()-t1}s')
        print('Your turn')

    if gamemode == "Human (sheep) vs Computer (wolf)" and not pawn_to_move[-1]:
        print('processing...')
        t1 = time.time()
        if len(squares)==8 or len(squares)==7:
            depth = 8
        elif len(squares)>5:
            depth = 9
        elif len(squares)>4:
            depth = 10
        elif len(squares)>3:
            depth = 11
        else:
            depth = 12
        # pc_move = output_best_move([list(squares),list(circles)],pawn_to_move[-1],depth)[1][0]
        with open("sheep.txt","w") as file:
            file.write(str(list(squares)))
        with open("wolf.txt","w") as file:
            file.write(str(list(circles)))
        subprocess.run([engine,str(0),str(depth)])
        pc_move = binary_to_cardesian()[1][0]
        if pc_move in squares:
            delete_square_by_coordinate(canvas,pc_move,square_size)
            squares.remove(pc_move)
            if len(squares)==0:
                root = tk.Tk()
                freeze_and_show_message('Wolf Wins!',root)
                # show_message_on_current_screen(root,'Wolf wins!')
        delete_all_circles(canvas,square_size,circles)
        add_circle(canvas, pc_move, square_size, circles)
        ready_to_move.append(False)
        pawn_to_move.append(True)
        print(f'Time: {time.time()-t1}s')
        print('Your turn')


    if notation in previous_light_circles_notations[-16:]:
        if ready_to_move[-1]:
            if notation in squares:
                delete_square_by_coordinate(canvas,notation,square_size)
                squares.remove(notation)
                if len(squares)==0:
                    root = tk.Tk()
                    freeze_and_show_message('Wolf Wins!',root)
                    # show_message_on_current_screen(root,'Wolf wins!')
            delete_all_circles(canvas,square_size,circles)
            add_circle(canvas, notation, square_size, circles)
            ready_to_move.append(False)
            pawn_to_move.append(True)
            previous_light_circles_notations.clear()

    # Check if the click is within the chessboard boundaries
    else:
        previous_light_circles_notations.clear()
        if 0 <= row < 8 and 0 <= col < 8:
            ready_to_move.append(False)
            if notation in circles and not pawn_to_move[-1]:
                # Draw gray circles in all squares of the clicked row and column
                ready_to_move.append(True)
                row, col = chess_notation_to_index(notation)
                # Going up
                while col < 7:
                    col += 1
                    row_notation = coordinate_converter(row,col)
                    if row_notation not in circles:
                        if unprotected(row_notation,squares):  # Avoid overlap with existing circles
                            circle_id = draw_light_circle(canvas, row, col, square_size)
                            light_circles.append(circle_id)  # Keep track of this circle
                            previous_light_circles_notations.append(row_notation)
                        else:
                            circle_id = draw_light_red_circle(canvas,row_notation,square_size)
                            light_red_circles.append(circle_id)
                    if row_notation in squares:
                        break
                row, col = chess_notation_to_index(notation)
                while col > -1: 
                    # Highlight row (same row, different columns)
                    row_notation = coordinate_converter(row, col)
                    if row_notation not in circles:  # Avoid overlap with existing circles
                        if unprotected(row_notation, squares):
                            circle_id = draw_light_circle(canvas, row, col, square_size)
                            light_circles.append(circle_id)  # Keep track of this circle
                            previous_light_circles_notations.append(row_notation)
                        else:
                            circle_id = draw_light_red_circle(canvas,row_notation,square_size)
                            light_red_circles.append(circle_id)
                    if row_notation in squares:
                        col = -1
                    col -= 1
                row, col = chess_notation_to_index(notation)
                while row > -1:
                    col_notation = coordinate_converter(row,col)
                    if col_notation not in circles:  # Avoid overlap with existing circles
                        if unprotected(col_notation, squares):
                            circle_id = draw_light_circle(canvas, row, col, square_size)
                            light_circles.append(circle_id)  # Keep track of this circle
                            previous_light_circles_notations.append(col_notation)
                        else:
                            circle_id = draw_light_red_circle(canvas,col_notation,square_size)
                            light_red_circles.append(circle_id)
                    if col_notation in squares:
                        break
                    row -= 1
                row, col = chess_notation_to_index(notation)
                while row < 8:
                    # Highlight column (same column, different rows)
                    col_notation = coordinate_converter(row, col)
                    if col_notation not in circles:  # Avoid overlap with existing circles
                        if unprotected(col_notation,squares):
                            circle_id = draw_light_circle(canvas, row, col, square_size)
                            light_circles.append(circle_id)  # Keep track of this circle
                            previous_light_circles_notations.append(col_notation)
                        else:
                            circle_id = draw_light_red_circle(canvas,col_notation,square_size)
                            light_red_circles.append(circle_id)
                    if col_notation in squares:
                        row = 7
                    row += 1
            elif notation in squares and pawn_to_move[-1]:
                light_square_anotation = notation[0]+str(int(notation[1])+1)
                if light_square_anotation in circles:
                    square_id = draw_light_red_square(canvas,light_square_anotation,square_size)
                    light_red_squares.append(square_id)
                else:
                    notation_to_delete.append(notation)
                    square_id = draw_light_square(canvas,light_square_anotation,square_size)
                    light_squares.append(square_id)
                    previous_light_squares_notations.append(light_square_anotation)
                    if int(notation[1])==1:
                        light_square_anotation = notation[0]+str(int(notation[1])+2)
                        if light_square_anotation in circles:
                            square_id = draw_light_red_square(canvas,light_square_anotation,square_size)
                            light_red_squares.append(square_id)
                        else:
                            square_id = draw_light_square(canvas,light_square_anotation,square_size)
                            light_squares.append(square_id)
                            previous_light_squares_notations.append(light_square_anotation)

            elif notation in previous_light_squares_notations[-2:] and pawn_to_move[-1]:
                add_square(canvas,notation,square_size,squares)
                pawn_to_move.append(False)
                delete_square_by_coordinate(canvas,notation_to_delete[-1],square_size)
                squares.remove(notation_to_delete[-1])
                light_squares.clear()
                previous_light_squares_notations.clear()
                if notation[1] == '8':
                    root = tk.Tk()  # This is the main Tkinter window
                    # root.geometry("600x400")
                    freeze_and_show_message('Sheeps win!',root)
            else:
                previous_light_squares_notations.clear()

# Function to draw a light gray circle in a specific square and return its ID
def draw_light_circle(canvas, row, col, square_size):
    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Calculate the coordinates for the circle (to fit inside the square)
    margin = 10  # Margin inside the square
    return canvas.create_oval(x1 + margin, y1 + margin, x2 - margin, y2 - margin, outline='gray', width=2)

def draw_light_square(canvas, notation, square_size):
    row, col = chess_notation_to_index(notation)
    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Calculate the coordinates for the circle (to fit inside the square)
    margin = 10  # Margin inside the square
    return canvas.create_rectangle(x1 + margin, y1 + margin, x2 - margin, y2 - margin, outline='gray', width=2)

def draw_light_red_square(canvas, notation, square_size):
    row, col = chess_notation_to_index(notation)
    # Calculate the top-left and bottom-right coordinates of the square
    x1 = col * square_size + 20
    y1 = row * square_size + 20
    x2 = x1 + square_size
    y2 = y1 + square_size
    
    # Calculate the coordinates for the circle (to fit inside the square)
    margin = 10  # Margin inside the square
    return canvas.create_rectangle(x1 + margin, y1 + margin, x2 - margin, y2 - margin, outline='red', width=2)

# Function to create the chessboard (same as before)
def create_chessboard_with_coordinates(size, square_size, gamemode=None):
    root = tk.Tk()
    canvas_size = size * square_size + 40  # Extra space for coordinates
    canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
    canvas.pack()

    # A set to track which squares have circles
    circles = set()
    squares = set()

    # Draw the chessboard squares
    for row in range(size):
        for col in range(size):
            x1 = col * square_size + 20
            y1 = row * square_size + 20
            x2 = x1 + square_size
            y2 = y1 + square_size
            color = "white" if (row + col) % 2 == 0 else "black"
            canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    # Draw coordinates (letters 'a' to 'h' and numbers '1' to '8')
    for i in range(size):
        # Horizontal labels (a-h)
        canvas.create_text((i + 0.5) * square_size + 20, 10, text=chr(ord('a') + i), font=('Arial', 16))
        canvas.create_text((i + 0.5) * square_size + 20, canvas_size - 10, text=chr(ord('a') + i), font=('Arial', 16))
        
        # Vertical labels (1-8)
        canvas.create_text(10, (i + 0.5) * square_size + 20, text=str(size - i), font=('Arial', 16))
        canvas.create_text(canvas_size - 10, (i + 0.5) * square_size + 20, text=str(size - i), font=('Arial', 16))

    # Add some example circles
    add_circle(canvas, "D8", square_size, circles)
    # add_circle(canvas, "E4", square_size, circles)

    # Add squares
    add_square(canvas, 'A1',square_size,squares)
    add_square(canvas, 'B1',square_size,squares)
    add_square(canvas, 'C1',square_size,squares)
    add_square(canvas, 'D1',square_size,squares)
    add_square(canvas, 'E1',square_size,squares)
    add_square(canvas, 'F1',square_size,squares)
    add_square(canvas, 'G1',square_size,squares)
    add_square(canvas, 'H1',square_size,squares)

    # Bind mouse click event to the function on_square_click
    # canvas.bind("<Button-1>", lambda event: on_square_click(event, canvas, square_size, circles))
    # canvas.bind("<Button-1>", lambda event: add_circle_on_click(event, canvas, square_size, circles))
    # canvas.bind("<Button-1>", lambda event: highlight_row_column_on_click(event, canvas, square_size, circles,squares))
    canvas.bind("<Button-1>", lambda event: highlight_row_column_on_click(event, canvas, square_size, circles,squares,gamemode))
    
    root.mainloop()
