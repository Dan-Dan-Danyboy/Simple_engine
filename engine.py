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

def simplify_outer_layers(input_list):
    # Initialize a list to hold the simplified result
    simplified_list = []
    
    # Recursive function to flatten the outer layers
    def flatten_outer(lst):
        # If the current list is a list of exactly two lists, return it as is
        if isinstance(lst, list) and len(lst) == 2 and all(isinstance(i, list) for i in lst):
            return [lst]
        # Otherwise, flatten the outer layers
        flattened = []
        for item in lst:
            if isinstance(item, list):
                flattened.extend(flatten_outer(item))  # Recursively flatten outer lists
            else:
                flattened.append(item)
        return flattened

    # Simplify the entire input list
    simplified_list = flatten_outer(input_list)
    
    return simplified_list

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

def make_tree(branches,positions):
    tree = [branches[0]]
    position_tree = [positions[0]]
    for i in range(len(branches)-1):
        if i == 0:
            tree.append(organize_list(branches[i+1],tree[i]))
            position_tree.append(organize_list(positions[i+1],tree[i]))
        else:
            if isinstance(simplify_list(tree[i])[0],int):
                tree.append(organize_list(branches[i+1],simplify_list(tree[i])))
                position_tree.append(organize_list(positions[i+1],simplify_list(tree[i])))
            else:
                tree.append(organize_list(
                    branches[i+1],
                    [sum(lst) for lst in simplify_list(tree[i])]
                ))
                position_tree.append(organize_list(
                    positions[i+1],
                    [sum(lst) for lst in simplify_list(tree[i])]
                ))
    return tree, position_tree

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

def find_best_move_2(positions,branches,sheep_to_move):
    num_iterations = len(positions)-1
    if num_iterations % 2 == 0:
        if sheep_to_move:
            sheep_to_move = False
        else:
            sheep_to_move = True
    puntuations = all_puntuations(positions[-1],branches[-1])
    print(puntuations)
    if sheep_to_move:
        puntuation = [max(move) for move in puntuations if len(move) != 0]
    else:
        puntuation = [min(move) for move in puntuations if len(move) != 0]
    for branch in reversed(branches):
        if sheep_to_move:
            posibilities = organize_list(puntuation,branch)
            puntuation = [max(move) for move in posibilities if len(move)!=0]
            sheep_to_move = False
        else:
            # print(len(puntuation))
            print(sum([sum(x) for x in branch]))
            posibilities = organize_list(puntuation,branch)
            puntuation = [min(move) for move in posibilities if len(move)!=0]
            sheep_to_move = True

    return positions[1][posibilities[0].index(puntuation[0])]

def all_puntuations(positions,branches):
    puntuations = []
    for position in positions:
        if all(not isinstance(i, list) for i in position[0]):
            puntuations.append(puntuacion(position[0]))
        else:
            puntuations.append(all_puntuations(position))
    puntuations = organize_list(puntuations,branches)
    return puntuations

def output_best_move(present,turn_sheep,depth=4):
    positions,branches = run_iterations(present,depth,turn_sheep)
    return find_best_move(positions,branches,turn_sheep)

def run_iterations_organized(present,depth,sheep_to_move):
    results_pos,n_outputs = [present],[]
    organized_results,branches = [],[]
    # results_points = [[puntuacion(present[0])]]
    for i in range(depth):
        t1 = time.time()
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
        organized_results.append(organize_list(pos,nou))
        branches.append(nou)
        if sheep_to_move:
            sheep_to_move = False
        else:
            sheep_to_move = True
        # print(i,time.time()-t1)
    # return results_pos,results_points,n_outputs
    # organized_branches = [branches[0]]
    # for i in range((len(branches))-1):
    #     organized_branches.append(organize_list(branches[i+1],branches[i]))
    tree_branches, tree_values = make_tree(branches,organized_results)
    return tree_values, tree_branches

def new_iteration(positions,move_made,branches,turn_sheep):
    index = simplify_list(positions[0]).index(move_made)
    new_tree,num_branches = [move_made],[]
    for future_move in positions[1:]:
        new_tree.append(simplify_list(future_move)[index])
    new_moves,new_branches = [],[]
    for branch in simplify_list(future_move)[index]:
        f,n = neural_processor(branch,turn_sheep)
        new_moves.append(f)
        new_branches.append(n)
    for branch in simplify_list(branches):
        num_branches.append(branch[index])
    new_tree.append(new_moves)
    num_branches.append(new_branches)
    return new_tree, num_branches

def save_list_as_array_joblib(sheep_to_move,depth=6):
    # Convert the list of lists into a NumPy array
    present = [['A1','B1','C1','D1','E1','F1','G1','H1'],['D8']]
    data_list,branches = run_iterations_organized(present,depth,sheep_to_move)
    if sheep_to_move:
        name1 = 'sheep_ite_tree_4.joblib' #Change to normal later
        name2 = 'branches_sheep_ite_tree_4.joblib'
    else:
        name1 = 'wolf_ite_tree_4.joblib' #Change to normal later
        name2 = 'branches_wolf_ite_tree_4.joblib'
    filename1 = os.path.join(os.getcwd(),'First_iterations',name1) 
    filename2 = os.path.join(os.getcwd(),'First_iterations',name2) 
    numpy_array1 = np.array(data_list)
    numpy_array2 = np.array(branches)

    # Save the NumPy array using Joblib with optional compression (e.g., compress=3)
    dump(numpy_array1, filename1, compress=3)  # compress=3 is a good balance between speed and file size
    dump(numpy_array2, filename2, compress=3)
    # print(f"Array successfully saved to {filename1}")

# Function to load the saved array back from the Joblib file
def load_array_from_joblib(filename):
    # Load the NumPy array from the Joblib file
    numpy_array = load(filename)
    # print(f"Array successfully loaded from {filename}")
    return numpy_array

# save_list_as_array_joblib(True)
# save_list_as_array_joblib(False)

# save_list_as_array_joblib(True,4)
# save_list_as_array_joblib(False,4)

positions = load_array_from_joblib(r"C:\Users\34673\Documents\Python\chess\First_iterations\wolf_ite_tree_4.joblib").tolist()
branches = load_array_from_joblib(r"C:\Users\34673\Documents\Python\chess\First_iterations\branches_wolf_ite_tree_4.joblib").tolist()

present = [['A1','B1','C1','E1','F1','G1','H1'],['D1']]
