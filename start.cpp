#include<iostream>
using namespace std ;
char board[8][8];
bool whiteTurn = true;  
void setupBoard() {
char initial[8][8] = {
    {'R','N','B','Q','K','B','N','R'},
    {'P','P','P','P','P','P','P','P'},
    {' ',' ',' ',' ',' ',' ',' ',' '},
    {' ',' ',' ',' ',' ',' ',' ',' '},
    {' ',' ',' ',' ',' ',' ',' ',' '},
    {' ',' ',' ',' ',' ',' ',' ',' '},
    {'p','p','p','p','p','p','p','p'},
    {'r','n','b','q','k','b','n','r'}
};
   for(int i=0 ;i<8 ;i++){
    for(int j=0 ;j<8;j++){
        board[i][j] = initial[i][j];
    }
   }
}

void printBoard() {
    cout << "\n    a b c d e f g h\n";
    cout << "  -------------------\n";

    for(int i = 0; i < 8; i++) {
        cout << 8 - i << " | ";
        for(int j = 0; j < 8; j++) {
            cout << board[i][j] << " ";
        }
        cout << "| " << 8 - i << endl;
    }

    cout << "  -------------------\n";
    cout << "    a b c d e f g h\n\n";
}

bool compareTrun(char piece)
{   
    if (whiteTurn && (piece >= 'A' && piece <= 'Z')) {
       return true;
        
    } else if (!whiteTurn && (piece >= 'a' && piece <= 'z')){
        return true;
    }
    return false;
}

void extractMove(string start, string end) {
    int startCol = start[0] - 'a'; // Convert 'a'-'h' to 0-7
    int startRow = 8 - (start[1] - '0'); // Convert '1'-'8' to 7-0
    int endCol = end[0] - 'a';
    int endRow = 8 - (end[1] - '0');

    cout << "Start: (" << startRow << ", " << startCol << ")\n";
    cout << "End: (" << endRow << ", " << endCol << ")\n";

    char piece = board[startRow][startCol];
    cout << "Piece to move: " << piece << endl;
        // Move the piece
    board[endRow][endCol] = piece;
    // make the perivous position empty
    board[startRow][startCol] = '.';
    // checking for turning 
    whiteTurn = !whiteTurn;
    printBoard();
}

int main() {
    setupBoard();
    printBoard();

    // take input 
    string start, end;

    cout << "Enter move (example: e2 e4): ";
    cin >> start >> end;

    cout << "You entered: " << start << " -> " << end << endl;
     extractMove(start , end);
    
     
    return 0;
}