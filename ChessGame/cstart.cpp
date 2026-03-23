#include <iostream>
#include <vector>
#include <string>
#include <cctype>
using namespace std;

vector<vector<char>> makeBoard() {
    return {
        {'r','n','b','q','k','b','n','r'},
        {'p','p','p','p','p','p','p','p'},
        {'.','.','.','.','.','.','.','.'},
        {'.','.','.','.','.','.','.','.'},
        {'.','.','.','.','.','.','.','.'},
        {'.','.','.','.','.','.','.','.'},
        {'P','P','P','P','P','P','P','P'},
        {'R','N','B','Q','K','B','N','R'}
    };
}

void printBoard(vector<vector<char>>& board) {
    cout << "\n  a b c d e f g h\n";
    for(int r=0;r<8;r++){
        cout << 8-r << " ";
        for(int c=0;c<8;c++)
            cout << board[r][c] << " ";
        cout << endl;
    }
}

char pieceColor(char p){
    if(p=='.') return 'n';
    return isupper(p) ? 'w' : 'b';
}

bool pathClear(vector<vector<char>>& board, int sr,int sc,int dr,int dc){
    int rstep = (dr>sr) ? 1 : (dr<sr ? -1 : 0);
    int cstep = (dc>sc) ? 1 : (dc<sc ? -1 : 0);
    int r = sr + rstep, c = sc + cstep;

    while(r!=dr || c!=dc){
        if(board[r][c] != '.') return false;
        r+=rstep; c+=cstep;
    }
    return true;
}

bool validPawn(vector<vector<char>>& board,int sr,int sc,int dr,int dc,char turn){
    int dir = (turn=='w') ? -1 : 1;
    int start = (turn=='w') ? 6 : 1;

    if(sc==dc && board[dr][dc]=='.'){
        if(dr==sr+dir) return true;
        if(sr==start && dr==sr+2*dir && board[sr+dir][sc]=='.')
            return true;
    }

    if(abs(dc-sc)==1 && dr==sr+dir){
        if(board[dr][dc]!='.' && pieceColor(board[dr][dc])!=turn)
            return true;
    }

    return false;
}

bool validMove(vector<vector<char>>& board,int sr,int sc,int dr,int dc,char turn){
    if(sr==dr && sc==dc) return false;

    char piece = board[sr][sc];
    if(piece=='.') return false;
    if(pieceColor(piece)!=turn) return false;
    if(pieceColor(board[dr][dc])==turn) return false;

    char p = tolower(piece);

    if(p=='p') return validPawn(board,sr,sc,dr,dc,turn);

    if(p=='n') return (abs(dr-sr)==2 && abs(dc-sc)==1) ||
                      (abs(dr-sr)==1 && abs(dc-sc)==2);

    if(p=='b') return abs(dr-sr)==abs(dc-sc) && pathClear(board,sr,sc,dr,dc);

    if(p=='r') return (sr==dr || sc==dc) && pathClear(board,sr,sc,dr,dc);

    if(p=='q') return ((sr==dr || sc==dc) ||
                      abs(dr-sr)==abs(dc-sc)) &&
                      pathClear(board,sr,sc,dr,dc);

    if(p=='k') return max(abs(dr-sr),abs(dc-sc))==1;

    return false;
}

void applyMove(vector<vector<char>>& board,int sr,int sc,int dr,int dc){
    board[dr][dc] = board[sr][sc];
    board[sr][sc] = '.';
}

bool kingCaptured(vector<vector<char>>& board){
    bool w=false,b=false;
    for(auto& r:board){
        for(char p:r){
            if(p=='K') w=true;
            if(p=='k') b=true;
        }
    }
    return !(w && b);
}

int main(){
    vector<vector<char>> board = makeBoard();
    char turn='w';

    while(true){
        printBoard(board);
        cout << (turn=='w'?"White":"Black") << " move (e2 e4): ";

        string s,d;
        cin>>s>>d;

        int sr = 8-(s[1]-'0');
        int sc = s[0]-'a';
        int dr = 8-(d[1]-'0');
        int dc = d[0]-'a';

        if(!validMove(board,sr,sc,dr,dc,turn)){
            cout<<"Invalid move!\n";
            continue;
        }

        applyMove(board,sr,sc,dr,dc);

        if(kingCaptured(board)){
            printBoard(board);
            cout<<(turn=='w'?"White":"Black")<<" wins!\n";
            break;
        }

        turn = (turn=='w') ? 'b' : 'w';
    }
}
