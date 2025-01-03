import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QFileDialog,
    QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtGui, QtCore, QtWidgets

# 假设您已经有这些 UI 文件
from Ui_start import Ui_MainWindow as Ui_StartWindow
from Ui_rules import Ui_RulesWindow
from Ui_mode import Ui_MainWindow as Ui_ModeWindow
from Ui_upload import Ui_MainWindow as Ui_UploadWindow
from Ui_difficulty import Ui_MainWindow as Ui_DifficultyWindow
from Ui_game import Ui_MainWindow as Ui_GameWindow
from Ui_manual_game import Ui_MainWindow as Ui_ManualGameWindow  # 确保有这个 UI 文件

class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 动态获取C程序的路径
        if hasattr(sys, '_MEIPASS'):
            self.c_programs_dir = os.path.join(sys._MEIPASS, 'c')
        else:
            self.c_programs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../c')

        # 创建并添加各个界面到 QStackedWidget
        self.start_ui = Ui_StartWindow()
        self.rules_ui = Ui_RulesWindow()
        self.mode_ui = Ui_ModeWindow()
        self.upload_ui = Ui_UploadWindow()
        self.difficulty_ui = Ui_DifficultyWindow()
        self.game_ui = Ui_GameWindow()
        self.manual_game_ui = Ui_ManualGameWindow()  # 新增 manual_game UI

        # 加载界面
        self.start_widget = QMainWindow()
        self.start_ui.setupUi(self.start_widget)
        self.stacked_widget.addWidget(self.start_widget)

        self.rules_widget = QMainWindow()
        self.rules_ui.setupUi(self.rules_widget)
        self.stacked_widget.addWidget(self.rules_widget)

        self.mode_widget = QMainWindow()
        self.mode_ui.setupUi(self.mode_widget)
        self.stacked_widget.addWidget(self.mode_widget)

        self.upload_widget = QMainWindow()
        self.upload_ui.setupUi(self.upload_widget)
        self.stacked_widget.addWidget(self.upload_widget)

        self.difficulty_widget = QMainWindow()
        self.difficulty_ui.setupUi(self.difficulty_widget)
        self.stacked_widget.addWidget(self.difficulty_widget)

        self.game_widget = QMainWindow()
        self.game_ui.setupUi(self.game_widget)
        self.stacked_widget.addWidget(self.game_widget)

        self.manual_game_widget = QMainWindow()  # 新增 manual_game widget
        self.manual_game_ui.setupUi(self.manual_game_widget)
        self.stacked_widget.addWidget(self.manual_game_widget)

        # 初始化 upload 页面时设置 sudoku_table 格式
        self.setup_sudoku_table(self.upload_ui.sudoku_table)
        self.upload_ui.sudoku_table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)  # 允许编辑

        # 初始隐藏 game_button
        self.upload_ui.game_button.setVisible(False)

        # 绑定按钮事件
        self.start_ui.rules.clicked.connect(self.show_rules)
        self.start_ui.game.clicked.connect(self.show_mode)

        self.rules_ui.rules_back.clicked.connect(self.show_main)
        self.mode_ui.upload.clicked.connect(self.show_upload)
        self.mode_ui.puzzle.clicked.connect(self.show_difficulty)
        self.mode_ui.mode_back.clicked.connect(self.show_main)
        self.difficulty_ui.difficulty_back.clicked.connect(self.show_mode)
        self.upload_ui.upload_back.clicked.connect(self.show_mode)

        # 绑定 upload 页面中的 game_button 以显示 manual_game 页面
        self.upload_ui.game_button.clicked.connect(self.show_manual_game)

        # 绑定难度按钮，传递不同的参数来生成对角线数独题目
        self.difficulty_ui.easy.clicked.connect(lambda: self.prepare_game("easy"))
        self.difficulty_ui.simple.clicked.connect(lambda: self.prepare_game("simple"))
        self.difficulty_ui.intermediate.clicked.connect(lambda: self.prepare_game("intermediate"))
        self.difficulty_ui.expert.clicked.connect(lambda: self.prepare_game("expert"))

        # 绑定 game 页面按钮
        self.game_ui.game_back.clicked.connect(self.show_difficulty)
        self.game_ui.check_button.clicked.connect(self.check_solution)
        self.game_ui.peek_button.clicked.connect(self.peek_solution)
        self.game_ui.show_button.clicked.connect(self.show_solution)

        # 绑定 manual_game 页面按钮（假设 manual_game 页面也有类似的按钮）
        self.manual_game_ui.game_back.clicked.connect(self.show_upload)  # 返回 upload 页面
        self.manual_game_ui.check_button.clicked.connect(self.check_solution_manual)
        self.manual_game_ui.peek_button.clicked.connect(self.peek_solution_manual)
        self.manual_game_ui.show_button.clicked.connect(self.show_solution_manual)

        # 绑定 upload 页面中的 set_button
        self.upload_ui.set_button.clicked.connect(self.set_puzzle)

        # 初始化 manual_game 页面时设置 sudoku_table 格式
        self.setup_sudoku_table(self.manual_game_ui.sudoku_table)
        self.manual_game_ui.sudoku_table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)  # 允许编辑

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game_time)

        self.peek_count = 0
        self.game_time_seconds = 0
        self.is_answer_shown = False
        self.answer_file_path = "solution.txt"
        self.previous_user_input = []  # 用于存储用户输入的状态

        # CNF 文件路径（用于 upload 和 manual_game 之间共享）
        self.upload_cnf_file = "uploaded_puzzle.cnf"

    # 通用方法来设置 sudoku_table 的格式
    def setup_sudoku_table(self, table):
        table.setRowCount(9)
        table.setColumnCount(9)
        table.horizontalHeader().setDefaultSectionSize(55)
        table.verticalHeader().setDefaultSectionSize(55)
        table.horizontalHeader().setMinimumSectionSize(55)
        table.verticalHeader().setMinimumSectionSize(55)
        table.setFont(QtGui.QFont("Arial", 22))
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 默认禁止编辑

        for row in range(9):
            for col in range(9):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                item.setForeground(QtGui.QBrush(Qt.blue))
                table.setItem(row, col, item)

        # 强制刷新 UI
        table.viewport().update()
        table.repaint()
        QtGui.QGuiApplication.processEvents()
        print(f"Set up sudoku_table for {table.objectName()}")

    # 显示 rules 页面
    def show_rules(self):
        self.stacked_widget.setCurrentWidget(self.rules_widget)

    # 显示 mode 页面
    def show_mode(self):
        self.stacked_widget.setCurrentWidget(self.mode_widget)

    # 显示 upload 页面
    def show_upload(self):
        self.stacked_widget.setCurrentWidget(self.upload_widget)

    # 显示 difficulty 页面
    def show_difficulty(self):
        self.stacked_widget.setCurrentWidget(self.difficulty_widget)

    # 显示 game 页面
    def show_game(self):
        self.game_ui.check_information.setVisible(False)
        table = self.game_ui.sudoku_table
        if table:
            self.setup_sudoku_table(table)
            table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)  # 允许编辑
        self.stacked_widget.setCurrentWidget(self.game_widget)

    # 显示 manual_game 页面
    def show_manual_game(self):
        self.manual_game_ui.check_information.setVisible(False)
        table = self.manual_game_ui.sudoku_table
        if table:
            self.setup_sudoku_table(table)
            table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)  # 允许编辑

            # 加载 CNF 文件到 manual_game 界面
            if os.path.exists(self.upload_cnf_file):
                self.load_puzzle_to_ui_manual(self.upload_cnf_file)
            else:
                QMessageBox.warning(self, "警告", "CNF 文件未找到。请先上传合法的数独格局。")
        self.stacked_widget.setCurrentWidget(self.manual_game_widget)

    # 显示 main 页面
    def show_main(self):
        self.stacked_widget.setCurrentWidget(self.start_widget)

    def get_selected_difficulty(self):
        """根据用户选择返回不同难度级别"""
        if self.difficulty_ui.easy.isChecked():
            return "easy"
        elif self.difficulty_ui.simple.isChecked():
            return "simple"
        elif self.difficulty_ui.intermediate.isChecked():
            return "intermediate"
        elif self.difficulty_ui.expert.isChecked():
            return "expert"
        return "easy"

    def prepare_game(self, difficulty):
        """根据选择的难度准备游戏"""
        self.timer.start(1000)
        self.peek_count = 0
        self.game_time_seconds = 0
        self.is_answer_shown = False
        self.game_ui.peek_count.setVisible(False)
        self.game_ui.game_time.setVisible(True)
        # 确定挖洞数量
        difficulty_levels = {
            "easy": "1",        # 假设"easy"对应20个挖洞
            "simple": "2",      # "simple" 对应30个挖洞
            "intermediate": "3",# "intermediate" 对应40个挖洞
            "expert": "4"       # "expert" 对应50个挖洞
        }
        # 获取数值型的难度级别
        difficulty_level = difficulty_levels.get(difficulty, "1")

        # 调用C程序生成对角线数独题目
        semantic_file_path = "generated_puzzle.cnf"  # 生成的语义编码CNF文件路径
        natural_file_path = "altered_puzzle.cnf"     # 生成的自然编码CNF文件路径
        generator_path = os.path.join(self.c_programs_dir, 'generate_diagonal_sudoku.exe')

        solver_path = os.path.join(self.c_programs_dir, 'sudoku_solver.exe')

        try:
            result = subprocess.run(
                [generator_path, difficulty_level, semantic_file_path, natural_file_path],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"Puzzle generation completed, CNF files saved to: {semantic_file_path} and {natural_file_path}")
            print(f"C program output: {result.stdout}")

            # 运行解算器
            result = subprocess.run(
                [solver_path, natural_file_path],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print("Solution file generated.")
            print(f"Solver output: {result.stdout}")

            # 转换解文件为数独网格格式
            if not self.convert_solution_to_grid("solution.cnf"):
                print("Error converting solution to grid format.")
                QMessageBox.critical(self, "错误", "转换解答时出错。")
                return

        except subprocess.CalledProcessError as e:
            print(f"Error generating puzzle or solution: {e}")
            print(f"C program error output: {e.stderr}")
            QMessageBox.critical(self, "错误", f"生成数独或解答时出错:\n{e.stderr}")
            return
        except Exception as e:
            print(f"Other error: {e}")
            QMessageBox.critical(self, "错误", f"其他错误:\n{e}")
            return

        # 清空游戏界面并显示新生成的数独
        self.show_game()
        self.display_puzzle(semantic_file_path)

    def convert_solution_to_grid(self, solution_cnf_path):
        """
        使用 cnf_to_grid.exe 将 CNF 格式的解转换为数独网格格式。
        """
        converter_path = os.path.join(self.c_programs_dir, 'cnf_to_grid.exe')

        grid_output_path = "solution.txt"  # 转换后的数独网格路径

        try:
            # 调用转换器程序
            result = subprocess.run(
                [converter_path, solution_cnf_path, grid_output_path],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"Solution converted and saved to: {grid_output_path}")
            print(f"C program output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting solution: {e}")
            print(f"C program error output: {e.stderr}")
            QMessageBox.critical(self, "错误", f"转换解答时出错:\n{e.stderr}")
            return False
        except Exception as e:
            print(f"Other error: {e}")
            QMessageBox.critical(self, "错误", f"其他错误:\n{e}")
            return False

        return True

    def display_puzzle(self, cnf_file_path):
        """将CNF格式的数独题目转换为可显示的数独格局"""
        parser_path = os.path.join(self.c_programs_dir, 'cnf_to_grid.exe')

        puzzle_file_path = "sudoku_puzzle.txt"  # 生成的数独格局路径

        try:
            result = subprocess.run(
                [parser_path, cnf_file_path, puzzle_file_path],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"Puzzle parsed and grid generated, saved to: {puzzle_file_path}")
            print(f"C program output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Parsing error: {e}")
            print(f"C program error output: {e.stderr}")
            QMessageBox.critical(self, "错误", f"解析数独题目时出错:\n{e.stderr}")
            return
        except Exception as e:
            print(f"Other error: {e}")
            QMessageBox.critical(self, "错误", f"其他错误:\n{e}")
            return

        # 在游戏界面显示生成的数独网格
        self.load_puzzle_to_ui(self.game_ui.sudoku_table, puzzle_file_path)

    def load_puzzle_to_ui(self, table, puzzle_file_path):
        """加载解析后的数独网格并显示在指定的 Sudoku 表格上"""
        try:
            with open(puzzle_file_path, 'r') as f:
                puzzle_lines = f.readlines()
            if not puzzle_lines:
                print("Error: Puzzle file is empty or not properly formatted.")
                QMessageBox.warning(self, "警告", "数独文件为空或格式不正确。")
                return

            print(f"Loaded puzzle from file: {puzzle_file_path}")
            table.setRowCount(9)
            table.setColumnCount(9)

            for row_idx, line in enumerate(puzzle_lines):
                numbers = line.strip().split()
                for col_idx, num in enumerate(numbers):
                    item = QTableWidgetItem("" if num == '0' else num)
                    item.setTextAlignment(Qt.AlignCenter)

                    if num != '0':  # 0 表示空格
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 禁止修改
                        item.setForeground(QtGui.QBrush(Qt.black))
                    else:
                        # 允许输入
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                        item.setForeground(QtGui.QBrush(Qt.blue))
                    table.setItem(row_idx, col_idx, item)

            # 强制刷新 UI
            table.viewport().update()
            table.repaint()

            # 调用 Qt 事件循环来确保 UI 刷新
            QtGui.QGuiApplication.processEvents()

            print("Successfully loaded puzzle into the UI.")  # 添加调试信息

        except Exception as e:
            print(f"Error loading puzzle to UI: {e}")
            QMessageBox.critical(self, "错误", f"加载数独到 UI 时出错:\n{e}")

    def load_puzzle_to_ui_manual(self, puzzle_file_path):
        """加载解析后的数独网格并显示在 manual_game 界面上"""
        self.load_puzzle_to_ui(self.manual_game_ui.sudoku_table, puzzle_file_path)
        print("Successfully loaded puzzle into the manual_game UI.")  # 添加调试信息

    def set_puzzle(self):
        """处理 upload 页面中 set_button 的点击事件"""
        # 读取当前 sudoku_table 的数独格局
        table = self.upload_ui.sudoku_table
        if not table:
            QMessageBox.warning(self, "警告", "数独表格未找到。")
            return

        sudoku_grid = []
        for row in range(9):
            row_data = []
            for col in range(9):
                item = table.item(row, col)
                if item and item.text().isdigit():
                    row_data.append(item.text())
                else:
                    row_data.append('0')  # 0 表示空格
            sudoku_grid.append(row_data)

        # 将数独格局保存到文件
        puzzle_file_path = "uploaded_puzzle.txt"
        try:
            with open(puzzle_file_path, 'w') as f:
                for row in sudoku_grid:
                    f.write(' '.join(row) + '\n')
            print(f"Uploaded puzzle saved to {puzzle_file_path}")
        except Exception as e:
            print(f"Error saving uploaded puzzle: {e}")
            QMessageBox.critical(self, "错误", f"保存数独格局时出错:\n{e}")
            return

        # 调用 judge 程序判断数独是否合法
        judge_program = os.path.join(self.c_programs_dir, 'judge.exe')  # 确保 judge 程序路径正确
        try:
            result = subprocess.run(
                [judge_program, puzzle_file_path],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            judge_output = result.stdout.strip()
            print(f"Judge program output: {judge_output}")
        except subprocess.CalledProcessError as e:
            print(f"Error running judge program: {e}")
            QMessageBox.critical(self, "错误", f"运行 judge 程序时出错:\n{e.stderr}")
            return
        except Exception as e:
            print(f"Other error: {e}")
            QMessageBox.critical(self, "错误", f"其他错误:\n{e}")
            return

        # 根据 judge 程序的输出判断是否合法
        if judge_output == "unique":
            # 合法
            self.upload_ui.legal_message.setText("恭喜你填出合法格局")
            self.upload_ui.legal_message.setStyleSheet("color: green; font-size: 16px;")
            self.upload_ui.legal_message.setVisible(True)

            # 显示 game_button
            self.upload_ui.game_button.setVisible(True)

            # 将数独格局转换为 CNF 文件并保存
            # 假设有一个程序 convert_to_cnf.exe 将数独格局转换为 CNF
            convert_program = os.path.join(self.c_programs_dir, 'convert_to_cnf.exe')
            try:
                result = subprocess.run(
                    [convert_program, puzzle_file_path, self.upload_cnf_file],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                print(f"Converted uploaded puzzle to CNF, saved to {self.upload_cnf_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting puzzle to CNF: {e}")
                QMessageBox.critical(self, "错误", f"转换数独格局到 CNF 时出错:\n{e.stderr}")
                return
            except Exception as e:
                print(f"Other error: {e}")
                QMessageBox.critical(self, "错误", f"其他错误:\n{e}")
                return
        else:
            # 不合法
            self.upload_ui.legal_message.setText("不合法，再试一试")
            self.upload_ui.legal_message.setStyleSheet("color: red; font-size: 16px;")
            self.upload_ui.legal_message.setVisible(True)

    def check_solution(self):
        """检查用户的答案是否正确"""
        if not os.path.exists(self.answer_file_path):
            print("Error: Solution file not found.")
            QMessageBox.warning(self, "警告", "解答文件未找到。")
            return

        correct_grid = []
        with open(self.answer_file_path, 'r') as f:
            correct_grid = [line.strip().split() for line in f.readlines()]

        table = self.game_ui.sudoku_table
        wrong_count = 0

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.text().isdigit():
                    if item.text() != correct_grid[row][col]:
                        wrong_count += 1

        if wrong_count == 0:
            self.game_ui.check_information.setText("填写全部正确！")
        else:
            self.game_ui.check_information.setText(f"您当前填错了 {wrong_count} 个数字。")

        self.game_ui.check_information.setVisible(True)
        QTimer.singleShot(5000, lambda: self.game_ui.check_information.setVisible(False))

    def check_solution_manual(self):
        """检查 manual_game 用户的答案是否正确"""
        if not os.path.exists(self.answer_file_path):
            print("Error: Solution file not found.")
            QMessageBox.warning(self, "警告", "解答文件未找到。")
            return

        correct_grid = []
        with open(self.answer_file_path, 'r') as f:
            correct_grid = [line.strip().split() for line in f.readlines()]

        table = self.manual_game_ui.sudoku_table
        wrong_count = 0

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.text().isdigit():
                    if item.text() != correct_grid[row][col]:
                        wrong_count += 1

        if wrong_count == 0:
            self.manual_game_ui.check_information.setText("填写全部正确！")
        else:
            self.manual_game_ui.check_information.setText(f"您当前填错了 {wrong_count} 个数字。")

        self.manual_game_ui.check_information.setVisible(True)
        QTimer.singleShot(5000, lambda: self.manual_game_ui.check_information.setVisible(False))

    def peek_solution(self):
        """偷看答案"""
        table = self.game_ui.sudoku_table  # 确保 table 在函数开始时定义

        if not self.is_answer_shown:
            self.peek_count += 1

            if not os.path.exists(self.answer_file_path):
                print("Error: Solution file not found.")
                QMessageBox.warning(self, "警告", "解答文件未找到。")
                return

            # 清空并保存用户当前输入的状态
            self.previous_user_input = []

            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                self.previous_user_input.append(row_data)

            # 显示答案
            with open(self.answer_file_path, 'r') as f:
                answer_lines = [line.strip().split() for line in f.readlines()]

            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and item.flags() & Qt.ItemIsEditable:  # 如果是可编辑单元格，则显示答案
                        item.setText(answer_lines[row][col])
                        item.setForeground(QtGui.QBrush(Qt.black))

            QTimer.singleShot(5000, lambda: self.hide_peek())

    def peek_solution_manual(self):
        """偷看答案 for manual_game"""
        table = self.manual_game_ui.sudoku_table  # 确保 table 在函数开始时定义

        if not self.is_answer_shown:
            self.peek_count += 1

            if not os.path.exists(self.answer_file_path):
                print("Error: Solution file not found.")
                QMessageBox.warning(self, "警告", "解答文件未找到。")
                return

            # 清空并保存用户当前输入的状态
            self.previous_user_input = []

            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                self.previous_user_input.append(row_data)

            # 显示答案
            with open(self.answer_file_path, 'r') as f:
                answer_lines = [line.strip().split() for line in f.readlines()]

            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and item.flags() & Qt.ItemIsEditable:  # 如果是可编辑单元格，则显示答案
                        item.setText(answer_lines[row][col])
                        item.setForeground(QtGui.QBrush(Qt.black))

            QTimer.singleShot(5000, lambda: self.hide_peek_manual())

    def hide_peek(self):
        """隐藏偷看的答案"""
        table = self.game_ui.sudoku_table
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.flags() & Qt.ItemIsEditable:  # 如果是可编辑单元格，则隐藏
                    # 恢复用户之前输入的内容
                    item.setText(self.previous_user_input[row][col] if self.previous_user_input else "")
                    item.setForeground(QtGui.QBrush(Qt.blue))  # 恢复为蓝色字体

    def hide_peek_manual(self):
        """隐藏偷看的答案 for manual_game"""
        table = self.manual_game_ui.sudoku_table
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.flags() & Qt.ItemIsEditable:  # 如果是可编辑单元格，则隐藏
                    # 恢复用户之前输入的内容
                    item.setText(self.previous_user_input[row][col] if self.previous_user_input else "")
                    item.setForeground(QtGui.QBrush(Qt.blue))  # 恢复为蓝色字体

    def show_solution(self):
        """显示完整的答案"""
        if not os.path.exists(self.answer_file_path):
            print("Error: Solution file not found.")
            QMessageBox.warning(self, "警告", "解答文件未找到。")
            return

        with open(self.answer_file_path, 'r') as f:
            answer_lines = [line.strip().split() for line in f.readlines()]

        table = self.game_ui.sudoku_table

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    item.setText(answer_lines[row][col])
                    item.setForeground(QtGui.QBrush(Qt.black))

        # 停止计时但显示时间
        self.timer.stop()
        self.game_ui.game_time.setVisible(True)  # 确保游戏时间显示
        self.game_ui.game_time.setText(f"游戏时间：{self.game_time_seconds // 60:02}:{self.game_time_seconds % 60:02}")

        # 显示偷看次数
        self.game_ui.peek_count.setVisible(True)
        self.game_ui.peek_count.setText(f"偷看次数：{self.peek_count}")

        self.is_answer_shown = True

    def show_solution_manual(self):
        """显示完整的答案 for manual_game"""
        if not os.path.exists(self.answer_file_path):
            print("Error: Solution file not found.")
            QMessageBox.warning(self, "警告", "解答文件未找到。")
            return

        with open(self.answer_file_path, 'r') as f:
            answer_lines = [line.strip().split() for line in f.readlines()]

        table = self.manual_game_ui.sudoku_table

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    item.setText(answer_lines[row][col])
                    item.setForeground(QtGui.QBrush(Qt.black))

        # 停止计时但显示时间
        self.timer.stop()
        self.manual_game_ui.game_time.setVisible(True)  # 确保游戏时间显示
        self.manual_game_ui.game_time.setText(f"游戏时间：{self.game_time_seconds // 60:02}:{self.game_time_seconds % 60:02}")

        # 显示偷看次数
        self.manual_game_ui.peek_count.setVisible(True)
        self.manual_game_ui.peek_count.setText(f"偷看次数：{self.peek_count}")

        self.is_answer_shown = True

    def update_game_time(self):
        """更新游戏时间"""
        if not self.is_answer_shown:
            self.game_time_seconds += 1
            minutes = self.game_time_seconds // 60
            seconds = self.game_time_seconds % 60
            self.game_ui.game_time.setText(f"游戏时间：{minutes:02}:{seconds:02}")

    def update_game_time_manual(self):
        """更新游戏时间 for manual_game"""
        if not self.is_answer_shown:
            self.game_time_seconds += 1
            minutes = self.game_time_seconds // 60
            seconds = self.game_time_seconds % 60
            self.manual_game_ui.game_time.setText(f"游戏时间：{minutes:02}:{seconds:02}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
