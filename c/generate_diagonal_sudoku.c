// generate_diagonal_sudoku.c

#include "head.h"

int solutionCount; // 全局变量来计数解的数量

// 检查数字 num 能否放置在 grid[row][col]
int isSafe(int grid[N][N], int row, int col, int num)
{
    int x, y;
    for (x = 0; x < N; x++)
        if (grid[row][x] == num || grid[x][col] == num)
            return 0;

    int startRow = row - row % 3, startCol = col - col % 3;
    for (x = 0; x < 3; x++)
        for (y = 0; y < 3; y++)
            if (grid[x + startRow][y + startCol] == num)
                return 0;


    return 1;
}

// 递归填充数独元素
int fillSudoku(int grid[N][N], int row, int col)
{
    if (row == N - 1 && col == N)
        return 1;
    if (col == N)
    {
        row++;
        col = 0;
    }
    if (grid[row][col] != UNASSIGNED)
        return fillSudoku(grid, row, col + 1);

    int num;
    for (num = 1; num <= N; num++)
    {
        if (isSafe(grid, row, col, num))
        {
            grid[row][col] = num;
            if (fillSudoku(grid, row, col + 1))
                return 1;
        }
        grid[row][col] = UNASSIGNED;
    }
    return 0;
}

// 计算数独的解的数量
void solveWithCount(int grid[N][N], int row, int col)
{
    if (row == N - 1 && col == N)
    {
        solutionCount++;
        return;
    }
    if (col == N)
    {
        row++;
        col = 0;
    }
    if (grid[row][col] != UNASSIGNED)
    {
        solveWithCount(grid, row, col + 1);
        return;
    }

    int num;
    for (num = 1; num <= N && solutionCount < 2; num++) // 只计算到两个解即可
    {
        if (isSafe(grid, row, col, num))
        {
            grid[row][col] = num;
            solveWithCount(grid, row, col + 1);
        }
        grid[row][col] = UNASSIGNED;
    }
}

// 验证当前数独是否只有一个解
int isUniqueSolution(int grid[N][N])
{
    solutionCount = 0;
    solveWithCount(grid, 0, 0);
    return solutionCount == 1;
}

// 随机生成第一行
void randomFirstRow(int grid[N][N])
{
    int i, j;
    int row[N];
    srand((unsigned)time(NULL));

    for (i = 0; i < N; i++)
    {
        row[i] = rand() % 9 + 1;
        j = 0;
        while (j < i)
        {
            if (row[i] == row[j])
            {
                row[i] = rand() % 9 + 1;
                j = 0;
            }
            else
                j++;
        }
    }

    for (i = 0; i < N; i++)
        grid[0][i] = row[i];
}

// 随机生成初盘，确保唯一解
void createStartingGrid(int grid[N][N], int holes)
{
    int x, y;
    int attempts = 0; // 增加尝试次数计数

    while (holes > 0) // 限制最大尝试次数为100
    {
        x = rand() % N;
        y = rand() % N;

        if (grid[x][y] == UNASSIGNED)
        {
            attempts++;
            continue; // 如果该位置已经是空格，则跳过
        }

        int backup = grid[x][y];
        grid[x][y] = UNASSIGNED;

        if (!isUniqueSolution(grid))
        {
            grid[x][y] = backup; // 如果不是唯一解，撤销操作
            attempts++;          // 增加尝试次数
        }
        else
        {
            holes--;
        }
    }
}

// 将语义编码转换为自然编码
int semanticToNatural(int i, int j, int k)
{
    return ((i - 1) * 81 + (j - 1) * 9 + k);
}

// 将自然编码转换为语义编码
void naturalToSemantic(int code, int *i, int *j, int *k)
{
    // 计算 k
    *k = (code % 9 == 0) ? 9 : code % 9;

    // 计算 i
    *i = (code - *k) / 81 + 1;

    // 计算 j
    *j = ((code - (*i - 1) * 81 - *k) / 9) + 1;
}

// 生成单元格约束
void addCellConstraints(FILE *file_nat)
{
    for (int i = 1; i <= 9; i++)
    {
        for (int j = 1; j <= 9; j++)
        {
            // 至少填入一个数字的子句
            for (int k = 1; k <= 9; k++)
            {
                fprintf(file_nat, "%d ", semanticToNatural(i, j, k));
            }
            fprintf(file_nat, "0\n");

            // 互斥性子句，确保每个单元格只能填一个数字
            for (int k1 = 1; k1 <= 8; k1++)
            {
                for (int k2 = k1 + 1; k2 <= 9; k2++)
                {
                    fprintf(file_nat, "-%d -%d 0\n", semanticToNatural(i, j, k1), semanticToNatural(i, j, k2));
                }
            }
        }
    }
}

// 生成行、列和3x3子盒约束
void addRowColumnBoxConstraints(FILE *file_nat)
{
    // 行约束和列约束
    for (int num = 1; num <= 9; num++)
    {
        for (int i = 1; i <= 9; i++)
        {
            // 行约束：每行包含1到9
            for (int j = 1; j <= 9; j++)
            {
                fprintf(file_nat, "%d ", semanticToNatural(i, j, num));
            }
            fprintf(file_nat, "0\n");

            // 列约束：每列包含1到9
            for (int j = 1; j <= 9; j++)
            {
                fprintf(file_nat, "%d ", semanticToNatural(j, i, num));
            }
            fprintf(file_nat, "0\n");

            // 互斥性约束：行和列中每个数字不重复
            for (int j1 = 1; j1 <= 8; j1++)
            {
                for (int j2 = j1 + 1; j2 <= 9; j2++)
                {
                    fprintf(file_nat, "-%d -%d 0\n", semanticToNatural(i, j1, num), semanticToNatural(i, j2, num)); // 行互斥
                    fprintf(file_nat, "-%d -%d 0\n", semanticToNatural(j1, i, num), semanticToNatural(j2, i, num)); // 列互斥
                }
            }
        }
    }

    // 3x3子盒约束
    for (int num = 1; num <= 9; num++)
    {
        for (int boxRow = 0; boxRow < 3; boxRow++)
        {
            for (int boxCol = 0; boxCol < 3; boxCol++)
            {
                for (int i = 1; i <= 3; i++)
                {
                    for (int j = 1; j <= 3; j++)
                    {
                        fprintf(file_nat, "%d ", semanticToNatural(boxRow * 3 + i, boxCol * 3 + j, num));
                    }
                }
                fprintf(file_nat, "0\n");

                // 3x3 子盒的唯一性约束
                for (int i1 = 1; i1 <= 3; i1++)
                {
                    for (int j1 = 1; j1 <= 3; j1++)
                    {
                        for (int i2 = i1; i2 <= 3; i2++)
                        {
                            for (int j2 = (i1 == i2 ? j1 + 1 : 1); j2 <= 3; j2++)
                            {
                                fprintf(file_nat, "-%d -%d 0\n", semanticToNatural(boxRow * 3 + i1, boxCol * 3 + j1, num), semanticToNatural(boxRow * 3 + i2, boxCol * 3 + j2, num));
                            }
                        }
                    }
                }
            }
        }
    }
}

void createSudokuToCNF(const char *semanticFile, const char *naturalFile, int holes)
{
    int grid[N][N] = {0};
    randomFirstRow(grid);   // 随机生成第一行
    fillSudoku(grid, 1, 0); // 递归生成后续行

    printf("Initial Sudoku Grid after filling:\n");
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            printf("%d ", grid[i][j]);
        }
        printf("\n");
    }

    // 生成初盘，确保唯一解
    createStartingGrid(grid, holes);

    printf("Sudoku Grid after creating starting grid with holes:\n");
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            printf("%d ", grid[i][j]);
        }
        printf("\n");
    }

    // 输出为语义编码的CNF文件
    FILE *file_sem = fopen(semanticFile, "w");
    if (!file_sem)
    {
        printf("无法创建语义输出文件: %s\n", semanticFile);
        return;
    }

    // 输出为自然编码的CNF文件
    FILE *file_nat = fopen(naturalFile, "w");
    if (!file_nat)
    {
        printf("无法创建自然输出文件: %s\n", naturalFile);
        return;
    }

    for (int row = 0; row < N; row++)
    {
        for (int col = 0; col < N; col++)
        {
            if (grid[row][col] != UNASSIGNED)
            {
                fprintf(file_sem, "%d%d%d 0\n", row + 1, col + 1, grid[row][col]);
                int natural_encoded = semanticToNatural(row + 1, col + 1, grid[row][col]);
                fprintf(file_nat, "%d 0\n", natural_encoded);
            }
        }
    }
    // 添加数独约束子句
    addCellConstraints(file_nat);
    addRowColumnBoxConstraints(file_nat);


    fclose(file_sem);
    fclose(file_nat);
    printf("数独已生成并保存至: %s 和 %s\n", semanticFile, naturalFile);
}

int main(int argc, char *argv[])
{
    if (argc != 4)
    {
        printf("Usage: %s <difficulty_level> <semantic_output.cnf> <natural_output.cnf>\n", argv[0]);
        return 1;
    }

    int difficulty = atoi(argv[1]);
    const char *semanticFile = argv[2];
    const char *naturalFile = argv[3];

    // 根据难度生成挖洞数目
    int maxHoles[] = {20, 30, 40, 50};
    int maxRange = 5;
    if (difficulty < 1 || difficulty > 4)
    {
        printf("Difficulty level should be between 1 and 4.\n");
        return 1;
    }

    srand((unsigned)time(NULL));
    int holes = maxHoles[difficulty - 1] - (rand() % (maxRange * 2 + 1) - maxRange);

    createSudokuToCNF(semanticFile, naturalFile, holes);
    return 0;
}
