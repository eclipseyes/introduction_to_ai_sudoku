// convert_to_cnf.c

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define N 9
#define UNASSIGNED 0

// 将语义编码 (i,j,k) 转换为自然编码
int semantic_to_natural(int i, int j, int k) {
    return (i - 1) * 81 + (j - 1) * 9 + k;
}

// 添加单元格约束（每个单元格至少一个数字，每个单元格至多一个数字）
void add_cell_constraints(FILE *f_nat) {
    for(int i =1;i<=9;i++) {
        for(int j=1;j<=9;j++) {
            // 至少一个数字
            for(int k=1;k<=9;k++) {
                fprintf(f_nat, "%d ", semantic_to_natural(i,j,k));
            }
            fprintf(f_nat, "0\n");
            
            // 至多一个数字
            for(int k1=1;k1<=8;k1++) {
                for(int k2=k1+1;k2<=9;k2++) {
                    fprintf(f_nat, "-%d -%d 0\n", semantic_to_natural(i,j,k1), semantic_to_natural(i,j,k2));
                }
            }
        }
    }
}

// 添加行约束（每行每个数字至少出现一次，每行每个数字至多出现一次）
void add_row_constraints(FILE *f_nat) {
    for(int i=1;i<=9;i++) {
        for(int k=1;k<=9;k++) {
            // 至少一个出现
            for(int j=1;j<=9;j++) {
                fprintf(f_nat, "%d ", semantic_to_natural(i,j,k));
            }
            fprintf(f_nat, "0\n");
            
            // 至多一个出现
            for(int j1=1;j1<=8;j1++) {
                for(int j2=j1+1;j2<=9;j2++) {
                    fprintf(f_nat, "-%d -%d 0\n", semantic_to_natural(i,j1,k), semantic_to_natural(i,j2,k));
                }
            }
        }
    }
}

// 添加列约束（每列每个数字至少出现一次，每列每个数字至多出现一次）
void add_column_constraints(FILE *f_nat) {
    for(int j=1;j<=9;j++) {
        for(int k=1;k<=9;k++) {
            // 至少一个出现
            for(int i=1;i<=9;i++) {
                fprintf(f_nat, "%d ", semantic_to_natural(i,j,k));
            }
            fprintf(f_nat, "0\n");
            
            // 至多一个出现
            for(int i1=1;i1<=8;i1++) {
                for(int i2=i1+1;i2<=9;i2++) {
                    fprintf(f_nat, "-%d -%d 0\n", semantic_to_natural(i1,j,k), semantic_to_natural(i2,j,k));
                }
            }
        }
    }
}

// 添加3x3子盒约束（每个子盒每个数字至少出现一次，每个子盒每个数字至多出现一次）
void add_box_constraints(FILE *f_nat) {
    for(int box_row=0; box_row<3; box_row++) {
        for(int box_col=0; box_col<3; box_col++) {
            for(int k=1;k<=9;k++) {
                // 至少一个出现
                for(int i=1;i<=3;i++) {
                    for(int j=1;j<=3;j++) {
                        fprintf(f_nat, "%d ", semantic_to_natural(box_row*3 + i, box_col*3 + j, k));
                    }
                }
                fprintf(f_nat, "0\n");
                
                // 至多一个出现
                for(int cell1=1; cell1<=8; cell1++) {
                    for(int cell2=cell1+1; cell2<=9; cell2++) {
                        int i1 = (cell1 -1)/3 +1;
                        int j1 = (cell1 -1)%3 +1;
                        int i2 = (cell2 -1)/3 +1;
                        int j2 = (cell2 -1)%3 +1;
                        fprintf(f_nat, "-%d -%d 0\n", semantic_to_natural(box_row*3 + i1, box_col*3 + j1, k), semantic_to_natural(box_row*3 + i2, box_col*3 + j2, k));
                    }
                }
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if(argc !=4){
        printf("Usage: %s <input_puzzle.txt> <semantic_cnf.cnf> <natural_cnf.cnf>\n", argv[0]);
        return 1;
    }
    char *input_puzzle = argv[1];
    char *semantic_cnf = argv[2];
    char *natural_cnf = argv[3];
    
    // 读取数独格局
    int grid[N][N];
    FILE *f_puzzle = fopen(input_puzzle, "r");
    if(!f_puzzle){
        perror("Error opening input puzzle file");
        return 1;
    }
    for(int i=0;i<N;i++) {
        for(int j=0;j<N;j++) {
            if(fscanf(f_puzzle, "%d", &grid[i][j]) !=1){
                printf("Invalid input format in puzzle file.\n");
                fclose(f_puzzle);
                return 1;
            }
        }
    }
    fclose(f_puzzle);
    
    // 写入语义编码的 CNF 文件
    FILE *f_sem = fopen(semantic_cnf, "w");
    if(!f_sem){
        perror("Error creating semantic CNF file");
        return 1;
    }
    for(int i=0;i<N;i++) {
        for(int j=0;j<N;j++) {
            int num = grid[i][j];
            if(num != UNASSIGNED){
                fprintf(f_sem, "%d%d%d 0\n", i+1, j+1, num);
            }
        }
    }
    fclose(f_sem);
    
    // 写入自然编码的 CNF 文件
    FILE *f_nat = fopen(natural_cnf, "w");
    if(!f_nat){
        perror("Error creating natural CNF file");
        return 1;
    }
    // 添加单元格约束
    add_cell_constraints(f_nat);
    // 添加行约束
    add_row_constraints(f_nat);
    // 添加列约束
    add_column_constraints(f_nat);
    // 添加3x3子盒约束
    add_box_constraints(f_nat);
    
    fclose(f_nat);
    
    printf("Successfully converted %s to CNF files: %s, %s\n", input_puzzle, semantic_cnf, natural_cnf);
    return 0;
}
