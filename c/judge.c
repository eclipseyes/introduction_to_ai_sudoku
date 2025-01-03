#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define N 9

// 检查当前数字是否可以放在指定位置
bool is_safe(int grid[N][N], int row, int col, int num) {
    for (int x = 0; x < N; x++) {
        // 检查行和列
        if (grid[row][x] == num || grid[x][col] == num) {
            return false;
        }
    }

    // 检查3x3子方块
    int start_row = row - row % 3, start_col = col - col % 3;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (grid[i + start_row][j + start_col] == num) {
                return false;
            }
        }
    }
    return true;
}

// 找到第一个未填的位置
bool find_unassigned_location(int grid[N][N], int *row, int *col) {
    for (*row = 0; *row < N; (*row)++) {
        for (*col = 0; *col < N; (*col)++) {
            if (grid[*row][*col] == 0) {
                return true;
            }
        }
    }
    return false;
}

// 解决数独问题，返回解决方案数量
int solve_sudoku(int grid[N][N], int *solution_count) {
    int row, col;

    // 如果没有未分配的空间，则解决方案已找到
    if (!find_unassigned_location(grid, &row, &col)) {
        (*solution_count)++;
        return *solution_count > 1; // 超过1个解就停止搜索
    }

    for (int num = 1; num <= 9; num++) {
        if (is_safe(grid, row, col, num)) {
            grid[row][col] = num;

            // 递归解决
            if (solve_sudoku(grid, solution_count)) {
                return true;
            }

            grid[row][col] = 0; // 撤销分配
        }
    }
    return false;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    int grid[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (fscanf(file, "%d", &grid[i][j]) != 1) {
                printf("Invalid input format\n");
                fclose(file);
                return 1;
            }
        }
    }
    fclose(file);

    int solution_count = 0;
    solve_sudoku(grid, &solution_count);

    if (solution_count == 0) {
        printf("No solution exists\n");
    } else if (solution_count == 1) {
        printf("unique");
    } else {
        printf("Multiple solutions exist\n");
    }

    return 0;
}
