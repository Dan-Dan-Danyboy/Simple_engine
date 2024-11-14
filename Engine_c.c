#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#define N 64
#define NN 16

// The letter indicate the column: A->0; C->2
// The number indicates the line: [0-7]
// A1->(col=0,lin=0)[0]; A6->(col=0;lin=5)[5]; B1->(col=1;lin=0)[8]

//N is the number of squares in a chessboard
//NN is the maximum number of outputs after one iteration a position can have
//s: sheep
//w: wolf
//open: indicates whether a ' has been found open or closed
//0-> Wolf to move
//1-> Sheep to move

void fill_with_zeros(int *squares);
int coordinate_conversor(char column, int line);
void add_piece(char piece, int *board);
void fill_board_sheep(int *squares, char column, int line);
void fill_board_wolf(int *squares, char column, int line);
int unprotected(int *squares, int coordinate);
int wolf_posibilities(int *squares, int (*posibilitie)[N]);
int sheep_posibilities(int *squares, int (*posibilitie)[N]);
int position_evaluation(int *squares);
int minmax(int depth, int isMaximizingPlayer, int alpha, int beta, int n, int *squares);

int main(int argc, char *argv[])
{
    if (argc < 2) {
        printf("Uso: %s <turn>\n", argv[0]);
        return 1; // Código de error si no se proporciona el argumento
    }

    // Convertir el argumento a un entero
    int turn = atoi(argv[1]), depth = atoi(argv[2]);
    int squares[N]={0},open=0,coordinate,j;
    int posibilities[NN][N]={0};
    char x,column;
    FILE *sheep, *wolf;

    sheep = fopen("sheep.txt","r");
    wolf = fopen("wolf.txt","r");

    while (fscanf(sheep,"%c", &x) != EOF)
    {
        if (x=='\'')
        {
            if (open==0)
            {
                open=1;
            }
            else
            {
                open = 0;
            }
        }
        else
        {
            if (open==1)
            {
                column = x;
                open = 2;
            }
            else if (open==2)
            {
                int line=x-'0';
                coordinate = coordinate_conversor(column,line);
                add_piece('s',&squares[coordinate]);
            }
        }
    }

    while (fscanf(wolf,"%c", &x) != EOF)
    {
        if (x=='\'')
        {
            if (open==0)
            {
                open=1;
            }
            else
            {
                open = 0;
            }
        }
        else
        {
            if (open==1)
            {
                column = x;
                open = 2;
            }
            else if (open==2)
            {
                int line=x-'0';
                coordinate = coordinate_conversor(column,line);
                add_piece('w',&squares[coordinate]);
            }
        }
    }

    fclose(sheep);
    fclose(wolf);
    minmax(depth,turn,INT_MIN,INT_MAX,depth,squares);
    return 1;
}

int coordinate_conversor(char column, int line)
{
    int col,coordinate;
    switch (column)
    {
        case 'A':
            col = 0;
            break;
        case 'B':
            col = 1;
            break;
        case 'C':
            col = 2;
            break;
        case 'D':
            col = 3;
            break;
        case 'E':
            col = 4;
            break;
        case 'F':
            col = 5;
            break;
        case 'G':
            col = 6;
            break;
        case 'H':
            col = 7;
            break;
    }
    coordinate = col*8+(line-1);
    return coordinate;
}

void add_piece(char piece, int *board)
{
    switch(piece)
    {
        case 's':
            *board = 1;
            break;
        case 'w':
            *board = -1;
            break;
    }
}

int unprotected(int *squares, int coordinate) //Return 0 if protected, 1 if not
{
    int colu = coordinate/8;
    if (colu != 0) //Checks on the left
    {
        if (*(squares+coordinate-9)==1) //squares initialized in the 0 index
        {
            return 0;
        }
    }
    if (colu != 7) //Checks on the right
    {
        if (*(squares+coordinate+7)==1)
        {
            return 0;
        }
    }
    return 1;
}

int wolf_posibilities(int *squares, int (*posibilitie)[N]) {
    int linee, columnn, j = 0;  // j indicates the possibility row in posibilitie

    for (int i = 0; i < N; i++) {
        if (squares[i] == -1) {  // Check if this square is a wolf
            linee = i % 8;
            columnn = i / 8;

            // Vertical check !
            for (int ii = linee - 1; ii >= 0; ii--) {
                if (unprotected(squares, columnn * 8 + ii) == 1) {
                    // Copy the vector `squares` into `posibilitie[j]`
                    memcpy(posibilitie[j], squares, N * sizeof(int));
                    posibilitie[j][i] = 0;
                    posibilitie[j][columnn * 8 + ii] = -1;
                    j++;
                }
                if (squares[i - (linee - ii)] == 1) {
                    break;
                }
            }

            // vertical check ¡
            for (int ii = linee + 1; ii <= 7; ii++) {
                if (ii==7)
                {
                    if (squares[i + (ii - linee)]==1) // If there's a pawn in the 8th row the game is over
                    {
                        return 0;
                    }
                }
                if (unprotected(squares, columnn * 8 + ii) == 1) {
                    memcpy(posibilitie[j], squares, N * sizeof(int));
                    posibilitie[j][i] = 0;
                    posibilitie[j][columnn * 8 + ii] = -1;
                    j++;
                }
                if (squares[i + (ii - linee)] == 1) {
                    break;
                }
            }

            // Horizontal check <-
            for (int ii = columnn - 1; ii >= 0; ii--) {
                if (linee == 7)
                {
                    if (squares[i - 8 * (columnn - ii)] == 1)
                    {
                        return 0; // End the game if there's a pawn in the last row
                    }
                }
                if (unprotected(squares, ii * 8 + linee) == 1) {
                    memcpy(posibilitie[j], squares, N * sizeof(int));
                    posibilitie[j][i] = 0;
                    posibilitie[j][ii * 8 + linee] = -1;
                    j++;
                }
                if (squares[i - 8 * (columnn - ii)] == 1) {
                    break;
                }
            }

            // Horizontal check ->
            for (int ii = columnn + 1; ii <= 7; ii++) {
                if (linee == 7)
                {
                    if (squares[i - 8 * (columnn - ii)] == 1)
                    {
                        return 0; // End the game if there's a pawn in the last row
                    }
                }
                if (unprotected(squares, ii * 8 + linee) == 1) {
//                    printf("Column %d\n", ii);
                    memcpy(posibilitie[j], squares, N * sizeof(int));
                    posibilitie[j][i] = 0;
                    posibilitie[j][ii * 8 + linee] = -1;
                    j++;
                }
                if (squares[i + 8 * (ii - columnn)] == 1) {
                    break;
                }
            }
        }
    }
    return j;
}

int sheep_posibilities(int *squares, int (*posibilitie)[N]) {
    int linee, columnn, j = 0;  // j indicates the possibility row in posibilitie

    for (int i = 0; i < N; i++) {
        if (squares[i] == 1) {
            linee = i % 8;
            columnn = i / 8;

            if (linee == 7) // If there's a pawn in the 8th row the game is over
            {
                return 0;
            }

            if (squares[i + 1] != -1) {
                linee++;
                // Copy entire `squares` array into `posibilitie[j]`
                memcpy(posibilitie[j], squares, N * sizeof(int));
                posibilitie[j][i] = 0;
                posibilitie[j][i+1] = 1;
                // Increment `j` to store the next possibility in the next row
                j++;

                // Further processing as per the example conditions
                if (linee == 1) {
                    if (squares[i + 2] != -1) {
                        linee++;
                        memcpy(posibilitie[j], squares, N * sizeof(int));
                        posibilitie[j][i] = 0;
                        posibilitie[j][i+2] = 1;
                        // Increment `j` to store the next possibility in the next row
                        j++;
                    }
                }
            }
        }
    }
    return j;
}

int position_evaluation(int *squares)
{
    int value=0,line;

    for (int i=0;i<N;i++)
    {
        if (*squares==1)
        {
            line = i%8;
            switch (line)
            {
                case 0:
                    value+=11;
                    break;
                case 1:
                    value+=12;
                    break;
                case 2:
                    value+=13;
                    break;
                case 3:
                    value+=15;
                    break;
                case 4:
                    value+=17;
                    break;
                case 5:
                    value+=23;
                    break;
                case 6:
                    value+=30;
                    break;
                case 7:
                    value+=80000;
                    break;
            }
            if (i/8 < 7)
            {
                for (int ii=5;ii<11;ii++)
                {
                    if (*(squares+ii)==1)
                    {
                        value += 20; // If there are pawns in parallel columns the puntuation increases, this teaches the engine strategy
                    }
                }
            }
            if (i/8>1)
            {
                for (int ii=11;ii>5;ii--)
                {
                    if (*(squares-ii)==1)
                    {
                        value += 20; // Checks the left column
                    }
                }
            }
        }
        squares++;
    }
    return value;
}

int minmax(int depth, int isMaximizingPlayer, int alpha, int beta, int n, int *squares) {
    if (depth == 0) {
        // Base case: evaluate position
        int eval = position_evaluation(squares);
        return eval;
    }

    int (*posibilitie)[N] = malloc(sizeof(int) * N * N); // Allocate memory for possible moves
    int numBranches;

    // Determine possible moves based on maximizing or minimizing
    if (isMaximizingPlayer) {
        numBranches = sheep_posibilities(squares, posibilitie);
    } else {
        numBranches = wolf_posibilities(squares, posibilitie);
    }

    // If there are no possible moves, evaluate the current position as if it were a terminal state
    if (numBranches == 0) {
        int eval = position_evaluation(squares);
        free(posibilitie);
        return eval;
    }

    int bestValue = isMaximizingPlayer ? INT_MIN : INT_MAX;
    int bestIndex = -1;  // Track the index of the best move for printing

    // Iterate through each branch/child node
    for (int i = 0; i < numBranches; i++) {
        int value = minmax(depth - 1, !isMaximizingPlayer, alpha, beta, n, posibilitie[i]);

        if (isMaximizingPlayer) {
            if (value > bestValue) {
                bestValue = value;
                bestIndex = i;
            }
            alpha = (alpha > bestValue) ? alpha : bestValue;  // Update alpha

            // Check if we can prune
            if (beta <= alpha) {
                free(posibilitie);
                return bestValue;
            }
        } else {
            if (value < bestValue) {
                bestValue = value;
                bestIndex = i;
            }
            beta = (beta < bestValue) ? beta : bestValue;  // Update beta

            // Check if we can prune
            if (beta <= alpha) {
                free(posibilitie);
                return bestValue;
            }
        }
    }

    // At the initial depth (root node), print the index and vector of the best move
    if (depth == n && bestIndex != -1) {
        FILE *solution;
        solution = fopen("solution.txt","w");
        fprintf(solution,"[");
        for (int j = 0; j < N; j++) {
            fprintf(solution,"%d", posibilitie[bestIndex][j]);
            if (j < N - 1) fprintf(solution,", ");
        }
        fprintf(solution,"]\n");
        fclose(solution);
    }

    free(posibilitie);
    return bestValue;
}
