from interfaz_user import coordinate_converter, unprotected
import os
import time
import numpy as np
from joblib import dump, load

def simplify_list(nested_list):
  """Simplifies a nested list containing a single list element.

  Args:
    nested_list: A nested list with a single list element.

  Returns:
    The simplified list.
  """

  if isinstance(nested_list, list) and len(nested_list) == 1 and isinstance(nested_list[0], list):
    return nested_list[0]
  else:
    return nested_list

def simplify_nested_list(nested_list):
    # Continue simplifying while the list contains exactly one list
    while isinstance(nested_list, list) and len(nested_list) == 1 and isinstance(nested_list[0], list):
        nested_list = nested_list[0]  # Remove one level of nesting
    return nested_list

def chess_notation_to_index(notation):
    # Convert the chess notation to row and column indices
    column = ord(notation[0].lower()) - ord('a')  # Convert 'a' to 'h' to 0 to 7
    row = 8 - int(notation[1])  # Convert '1' to '8' to 7 to 0
    return row, column

def possible_circle_moves(circles,squares):
    possible_moves = []
    notation = [circle for circle in circles][0]
    row, col = chess_notation_to_index(notation)
    # Going up
    while col < 7:
        col += 1
        row_notation = coordinate_converter(row,col)
        if row_notation not in circles:
            if unprotected(row_notation,squares):  # Avoid overlap with existing circles
                possible_moves.append(row_notation)
        if row_notation in squares:
            break
    row, col = chess_notation_to_index(notation)
    while col > -1: 
        # Highlight row (same row, different columns)
        row_notation = coordinate_converter(row, col)
        if row_notation not in circles:  # Avoid overlap with existing circles
            if unprotected(row_notation, squares):
                possible_moves.append(row_notation)
        if row_notation in squares:
            col = -1
        col -= 1
    row, col = chess_notation_to_index(notation)
    while row > -1:
        col_notation = coordinate_converter(row,col)
        if col_notation not in circles:  # Avoid overlap with existing circles
            if unprotected(col_notation, squares):
                possible_moves.append(col_notation)
        if col_notation in squares:
            break
        row -= 1
    row, col = chess_notation_to_index(notation)
    while row < 8:
        # Highlight column (same column, different rows)
        col_notation = coordinate_converter(row, col)
        if col_notation not in circles:  # Avoid overlap with existing circles
            if unprotected(col_notation,squares):
                possible_moves.append(col_notation)
        if col_notation in squares:
            row = 7
        row += 1
    return possible_moves

def possible_square_moves(circles,squares):
    future = []
    for sheep in squares:
        future_posibility = sheep[0]+str(int(sheep[1])+1)
        if not future_posibility in circles:
            future_positions = [future_posibility if x == sheep else x for x in squares]
            future.append(future_positions)
            if sheep[1] == '1':
                future_posibility = sheep[0]+str(int(sheep[1])+2)
                if not future_posibility in circles:
                    future_positions = [future_posibility if x == sheep else x for x in squares]
                    future.append(future_positions)
    return future

def count_parallel_squares(squares_list, target_square):
    # Convert the target_square notation to row and column indices
    target_row, target_col = chess_notation_to_index(target_square)
    
    parallel_count = 0  # Count of valid parallel squares

    # Iterate over each square in the list
    for square in squares_list:
        row, col = chess_notation_to_index(square)

        # Check for squares in the same column (diagonal checking)
        if col == target_col:  # Same column for diagonal reach
            row_diff = abs(row - target_row)  # Calculate the row difference
            if row_diff <= 2:  # Within 2 rows (1 or 2)
                parallel_count += 1  # Count this square
        
        # Check for squares in parallel columns (adjacent columns)
        elif abs(col - target_col) == 1:  # Column is parallel
            row_diff = abs(row - target_row)  # Calculate the row difference
            if row_diff <= 2:  # Within 2 rows
                parallel_count += 1  # Count this square

    return parallel_count  # Return the total count of valid parallel squares

def puntuacion(sheeps):
    puntos_sheep, puntos_wolf = 0,8
    valor_columna = {'1':0.5,'2':0.7,'3':0.9,'4':1.1,'5':1.3,'6':1.6,'7':3,'8':100,'9':200,'10':400,'11':800,'12':1500,'13':3000}
    valor_conected = {1:0.9,2:1.6,3:2.3}

    if len(sheeps)==0:
        return -100

    for sheep in sheeps:
        puntos_sheep += valor_columna[sheep[1]]*valor_conected[count_parallel_squares(sheeps,sheep)]
    puntuacion = puntos_sheep-puntos_wolf

    return puntuacion

def organize_list(lst1, lst2):
    result = []
    index = 0
    for size in lst2:
        result.append(lst1[index:index + size])
        index += size
    return result

def find_sublist_index(nested_list, target_list):
    for idx, sublist in enumerate(nested_list):
        if sublist == target_list:
            return idx
        elif isinstance(sublist, list):  # Recursively check if it's a list
            found = find_sublist_index(sublist, target_list)
            if found is not None:
                return idx
    return None  # Return None if the target is not found

def neural_processor(present,turn_sheep,first_ite=False):
    future,num_outputs = [],[]
    # puntuaciones = []
    if first_ite:
        if turn_sheep:
            sheep,wolf = present[0],present[1]
            pos_square_moves = possible_square_moves(wolf,sheep)
            num_outputs.append(len(pos_square_moves))
            for move in pos_square_moves:
                future.append([move,wolf])
                # puntuaciones.append(puntuacion(move))
        else:
            sheep,wolf = present[0],present[1]
            if all(not isinstance(i, list) for i in sheep):
                pos_circ_moves = possible_circle_moves(wolf,sheep)
                num_outputs.append(len(pos_circ_moves))
                for move in pos_circ_moves:
                    if move[1] == '8':
                        sheeps = sheep
                    else:
                        sheeps = [shep for shep in sheep if not shep == move]
                    future.append([sheeps,[move]])
                    # puntuaciones.append(puntuacion(sheeps))
    else:
        if turn_sheep:
            for thing in present:
                sheep,wolf = thing[0],thing[1]
                if all(not isinstance(i, list) for i in sheep): 
                    pos_square_moves = possible_square_moves(wolf,sheep)
                    num_outputs.append(len(pos_square_moves))
                    for move in pos_square_moves:
                        future.append([move,wolf])
                        # puntuaciones.append(puntuacion(move))
                else:
                    f,n = neural_processor(sheep,True)
                    future.append(f)
                    # puntuaciones.append(p)
                    num_outputs.append(n)
        else:
            for thing in present:
                sheep,wolf = thing[0],thing[1]
                if all(not isinstance(i, list) for i in sheep):
                    pos_circ_moves = possible_circle_moves(wolf,sheep)
                    num_outputs.append(len(pos_circ_moves))
                    for move in pos_circ_moves:
                        if move[1] == '8':
                            sheeps = sheep
                        else:
                            sheeps = [shep for shep in sheep if not shep == move]
                        future.append([sheeps,[move]])
                        # puntuaciones.append(puntuacion(sheeps))
                else:
                    f,n = neural_processor(wolf,False)
                    future.append(f)
                    # puntuaciones.append(p)
                    num_outputs.append(n)
    # return future,puntuaciones,num_outputs
    return future,num_outputs

def run_iterations(present,depth,sheep_to_move):
    results_pos,n_outputs = [present],[]
    # results_points = [[puntuacion(present[0])]]
    for i in range(depth):
        if i == 0:
            # pos,poi,nou = neural_processor(results_pos[i],sheep_to_move,True)
            pos,nou = neural_processor(results_pos[i],sheep_to_move,True)
            results_pos.append(pos)
            # results_points.append(poi)
            n_outputs.append(nou)
        else:
            # pos,poi,nou = neural_processor(results_pos[i],sheep_to_move)
            pos,nou = neural_processor(results_pos[i],sheep_to_move)
            results_pos.append(pos)
            # results_points.append(poi)
            n_outputs.append(nou)
        if sheep_to_move:
            sheep_to_move = False
        else:
            sheep_to_move = True
    # return results_pos,results_points,n_outputs
    return results_pos,n_outputs

def find_best_move(positions,branches,sheep_to_move):
    num_iterations = len(positions)-1
    if num_iterations % 2 == 0:
        if sheep_to_move:
            sheep_to_move = False
        else:
            sheep_to_move = True
    puntuation = [puntuacion(position[0]) for position in positions[-1]]
    for branch in reversed(branches):
        if sheep_to_move:
            posibilities = organize_list(puntuation,branch)
            puntuation = [max(move) for move in posibilities if len(move)!=0]
            sheep_to_move = False
        else:
            posibilities = organize_list(puntuation,branch)
            puntuation = [min(move) for move in posibilities if len(move)!=0]
            sheep_to_move = True

    return positions[1][posibilities[0].index(puntuation[0])]

def output_best_move(present,turn_sheep,depth=4):
    positions,branches = run_iterations(present,depth,turn_sheep)
    return find_best_move(positions,branches,turn_sheep)
