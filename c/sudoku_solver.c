// sudoku_solver.c

#include "head.h"

// DPLL 求解器
status DpllSolver(ClauseNode *s, int *truth_table)
{
    ClauseNode *s_tmp = s;
    ClauseNode *unit_clause = IsUnitClause(s_tmp);

    printf("Starting DPLL solver...\n");

    while (unit_clause)
    {
        RecordTruth(unit_clause, truth_table);
        int var = unit_clause->right->data;

        RemoveVar(s, var);

        if (s->down == NULL)
        {
            
            return FOUND;
        }
        else if (IsEmptyClause(s))
        {
           
            return NOTFOUND;
        }

        s_tmp = s;
        unit_clause = IsUnitClause(s_tmp);
    }

    int var = PickVar(s);

    if (DpllSolver(AddClause(CopyS(s), var), truth_table))
    {
        
        return FOUND;
    }


    return DpllSolver(AddClause(s, -var), truth_table);
}

// 添加子句至子句集
ClauseNode *AddClause(ClauseNode *s, int var)
{
    ClauseNode *c_tmp = (ClauseNode *)malloc(sizeof(ClauseNode));
    c_tmp->right = (LiteralNode *)malloc(sizeof(LiteralNode));
    c_tmp->right->data = var;
    c_tmp->right->right = NULL;
    c_tmp->down = s->down;
    s->down = c_tmp;
    return s;
}

// 判断是否存在单子句
ClauseNode *IsUnitClause(ClauseNode *s)
{
    ClauseNode *c_tmp = s;
    while (c_tmp)
    {
        if (c_tmp->right && !c_tmp->right->right)
            return c_tmp;
        c_tmp = c_tmp->down;
    }
    return NULL;
}

// 复制子句集
ClauseNode *CopyS(ClauseNode *s)
{
    ClauseNode *s_new, *c_tmp, *s_origin = s->down;
    s_new = (ClauseNode *)malloc(sizeof(ClauseNode));
    s_new->right = NULL;
    c_tmp = s_new;

    while (s_origin)
    {
        c_tmp->down = CopyClause(s_origin);
        c_tmp = c_tmp->down;
        s_origin = s_origin->down;
    }
    return s_new;
}

// 复制单个子句
ClauseNode *CopyClause(ClauseNode *s)
{
    ClauseNode *clause_tmp = (ClauseNode *)malloc(sizeof(ClauseNode));
    LiteralNode *literal_tmp, *s_tmp = s->right;

    clause_tmp->down = NULL;
    clause_tmp->right = NULL;

    if (s_tmp)
    {
        literal_tmp = (LiteralNode *)malloc(sizeof(LiteralNode));
        literal_tmp->data = s_tmp->data;
        literal_tmp->right = NULL;
        s_tmp = s_tmp->right;
        clause_tmp->right = literal_tmp;
    }

    while (s_tmp)
    {
        literal_tmp->right = (LiteralNode *)malloc(sizeof(LiteralNode));
        literal_tmp->right->data = s_tmp->data;
        literal_tmp->right->right = NULL;
        literal_tmp = literal_tmp->right;
        s_tmp = s_tmp->right;
    }
    return clause_tmp;
}

// 删除子句
ClauseNode *DeleteClause(ClauseNode *s)
{
    ClauseNode *c_tmp = s;
    LiteralNode *l;
    while (s->right)
    {
        l = s->right;
        s->right = s->right->right;
        free(l);
    }
    s = s->down;
    free(c_tmp);
    return s;
}

// 删除负变元
ClauseNode *DeleteLiteral(ClauseNode *s, int var)
{
    LiteralNode *l = s->right, *l_tmp;

    if (l->data == -var)
    {
        l_tmp = s->right->right;
        free(l);
        s->right = l_tmp;
        return s;
    }
    else if (l->data == var)
    {
        return NULL;
    }

    while (l)
    {
        if (l->right && l->right->data == -var)
        {
            l_tmp = l->right;
            l->right = l->right->right;
            free(l_tmp);
        }
        else if (l->right && l->right->data == var)
        {
            return NULL;
        }
        l = l->right;
    }
    return s;
}

// 判断是否存在空子句
status IsEmptyClause(ClauseNode *s)
{
    ClauseNode *c_tmp = s->down;
    while (c_tmp)
    {
        if (!c_tmp->right)
            return YES;
        c_tmp = c_tmp->down;
    }
    return NO;
}

// 记录单子句中元素的真值
status RecordTruth(ClauseNode *s, int *truth_table)
{
    int idx = abs(s->right->data) - 1;
    if (s->right->data > 0)
        truth_table[idx] = 1;
    else
        truth_table[idx] = 0;
    return OK;
}

// 删除变元所在子句与负变元
status RemoveVar(ClauseNode *s, int var)
{
    ClauseNode *c_tmp = s->down, *last_c_tmp = s;
    while (c_tmp)
    {
        c_tmp = DeleteLiteral(c_tmp, var);
        if (c_tmp == NULL)
        {
            c_tmp = DeleteClause(last_c_tmp->down);
            last_c_tmp->down = c_tmp;
            continue;
        }
        if (c_tmp == NULL)
            break;
        last_c_tmp = c_tmp;
        c_tmp = c_tmp->down;
    }
    return OK;
}

// 选取一个变元
int PickVar(ClauseNode *s)
{
    int var = s->down->right->data;
    return var;
}

// 打印子句集
status Print(ClauseNode *s)
{
    ClauseNode *c_tmp = s->down;
    LiteralNode *l_tmp;
    printf("\n-----Start-----\n");
    while (c_tmp)
    {
        l_tmp = c_tmp->right;
        while (l_tmp)
        {

            l_tmp = l_tmp->right;
        }
        if (c_tmp->right)
            printf("\n");
        else
            printf("空\n");
        c_tmp = c_tmp->down;
    }
    printf("------End------\n");
    return OK;
}

// 解析 CNF 文件
ClauseNode *CnfParser(int *literal_num, char *filename, int *max_var)
{
    FILE *file = fopen(filename, "r");
    if (!file)
    {
        printf("Error opening file: %s\n", filename);
        return NULL;
    }

    ClauseNode *cnf = (ClauseNode *)malloc(sizeof(ClauseNode));
    cnf->down = NULL;
    cnf->right = NULL;
    *max_var = 0;

    char line[11000];
    while (fgets(line, sizeof(line), file))
    {
        if (line[0] == 'c' || line[0] == 'p')
        {
            continue;
        }
        ClauseNode *new_clause = (ClauseNode *)malloc(sizeof(ClauseNode));
        new_clause->down = NULL;
        new_clause->right = NULL;

        char *token = strtok(line, " ");
        while (token)
        {
            int lit = atoi(token);
            if (lit == 0)
                break;
            if (abs(lit) > *max_var)
                *max_var = abs(lit); // 记录最大变元编号
            LiteralNode *literal = (LiteralNode *)malloc(sizeof(LiteralNode));
            literal->data = lit;
            literal->right = new_clause->right;
            new_clause->right = literal;

            token = strtok(NULL, " ");
        }

        new_clause->down = cnf->down;
        cnf->down = new_clause;
    }
    fclose(file);
    return cnf;
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

// 主程序入口

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <cnf file path>\n", argv[0]);
        return 1;
    }

    char cnf_path[256];
    strcpy(cnf_path, argv[1]);
    int truth_table[N * N * N] = {0}; // 调整为适应9x9数独
    int max_var = 0;

    ClauseNode *cnf = CnfParser(truth_table, cnf_path, &max_var);

    if (!cnf)
    {
        fprintf(stderr, "Error reading CNF file: %s\n", cnf_path);
        return 1;
    }

    status result = DpllSolver(cnf, truth_table);

    // 打开语义编码的输出文件
    FILE *output_file = fopen("solution.cnf", "w"); // 固定输出文件路径
    if (!output_file)
    {
        fprintf(stderr, "Cannot open output file.\n");
        return 1;
    }

    // 打开自然编码的输出文件
    FILE *natural_output_file = fopen("natural_solution.cnf", "w");
    if (!natural_output_file)
    {
        fprintf(stderr, "Cannot open natural output file.\n");
        fclose(output_file);
        return 1;
    }

    if (result == FOUND)
    {
        for (int i = 0; i < N * N * N; i++)
        {
            if (truth_table[i] == 1)
            {

                // 将自然编码转换为语义编码
                int row, col, num;
                naturalToSemantic(i + 1, &row, &col, &num);

                // 写入语义编码文件
                fprintf(output_file, "%d%d%d 0\n", row, col, num);

                // 写入自然编码文件
                fprintf(natural_output_file, "%d 0\n", i + 1);
            }
        }
    }
    else
    {
        fprintf(output_file, "s 0\n");
        fprintf(natural_output_file, "s 0\n");
    }

    fclose(output_file);
    fclose(natural_output_file);

    Print(cnf);

    return 0;
}
