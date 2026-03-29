#include <iostream>
#include <vector>
#include <queue>
#include <cstring>

using namespace std;

class MazeSolver {
private:
    vector<vector<char>> grid;
    int height, width;
    int start_r, start_c, goal_r, goal_c;
    
    bool isValid(int r, int c) {
        return r >= 0 && r < height && c >= 0 && c < width && grid[r][c] == ' ';
    }
    
public:
    MazeSolver(int h, int w) : height(h), width(w) {
        grid.resize(h, vector<char>(w));
    }
    
    void setGrid(const char* gridData) {
        int idx = 0;
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                grid[i][j] = gridData[idx++];
            }
        }
    }
    
    void setPositions(int sr, int sc, int gr, int gc) {
        start_r = sr; start_c = sc;
        goal_r = gr; goal_c = gc;
    }
    
    // BFS Algorithm
    void solveBFS(int* result, int* pathLength) {
        vector<vector<bool>> visited(height, vector<bool>(width, false));
        vector<vector<pair<int, int>>> parent(height, vector<pair<int, int>>(width, {-1, -1}));
        
        queue<pair<int, int>> q;
        q.push({start_r, start_c});
        visited[start_r][start_c] = true;
        
        while (!q.empty()) {
            auto [r, c] = q.front();
            q.pop();
            
            if (r == goal_r && c == goal_c) break;
            
            int dirs[4][2] = {{-1,0}, {1,0}, {0,-1}, {0,1}};
            for (int i = 0; i < 4; i++) {
                int nr = r + dirs[i][0];
                int nc = c + dirs[i][1];
                if (isValid(nr, nc) && !visited[nr][nc]) {
                    visited[nr][nc] = true;
                    parent[nr][nc] = {r, c};
                    q.push({nr, nc});
                }
            }
        }
        
        // Reconstruct path
        vector<pair<int, int>> path;
        int cr = goal_r, cc = goal_c;
        while (cr != -1 && cc != -1) {
            path.push_back({cr, cc});
            auto [pr, pc] = parent[cr][cc];
            cr = pr; cc = pc;
        }
        reverse(path.begin(), path.end());
        
        *pathLength = path.size();
        for (int i = 0; i < path.size(); i++) {
            result[i * 2] = path[i].first;
            result[i * 2 + 1] = path[i].second;
        }
    }
    
    // DFS Algorithm
    void solveDFS(int* result, int* pathLength) {
        vector<vector<bool>> visited(height, vector<bool>(width, false));
        vector<pair<int, int>> path;
        
        function<bool(int, int)> dfs = [&](int r, int c) -> bool {
            visited[r][c] = true;
            path.push_back({r, c});
            
            if (r == goal_r && c == goal_c) return true;
            
            int dirs[4][2] = {{-1,0}, {1,0}, {0,-1}, {0,1}};
            for (int i = 0; i < 4; i++) {
                int nr = r + dirs[i][0];
                int nc = c + dirs[i][1];
                if (isValid(nr, nc) && !visited[nr][nc]) {
                    if (dfs(nr, nc)) return true;
                }
            }
            path.pop_back();
            return false;
        };
        
        dfs(start_r, start_c);
        
        *pathLength = path.size();
        for (int i = 0; i < path.size(); i++) {
            result[i * 2] = path[i].first;
            result[i * 2 + 1] = path[i].second;
        }
    }
};

MazeSolver* solver = nullptr;

extern "C" {
    void initSolver(int h, int w) {
        solver = new MazeSolver(h, w);
    }
    
    void setGridData(const char* gridData) {
        if (solver) solver->setGrid(gridData);
    }
    
    void setPositions(int sr, int sc, int gr, int gc) {
        if (solver) solver->setPositions(sr, sc, gr, gc);
    }
    
    void solveBFS(int* result, int* pathLength) {
        if (solver) solver->solveBFS(result, pathLength);
    }
    
    void solveDFS(int* result, int* pathLength) {
        if (solver) solver->solveDFS(result, pathLength);
    }
    
    void cleanupSolver() {
        if (solver) {
            delete solver;
            solver = nullptr;
        }
    }
}
