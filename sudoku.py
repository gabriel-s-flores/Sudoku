import sys
import numpy as np
import random
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QLineEdit, QLabel, QComboBox, QMainWindow, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QFont

class SudokuGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()  # Initialize the user interface
        self.game_data = None  # Initialize game data to None
        self.errors = 0  # Initialize errors counter to 0

    def initUI(self):
        """Initialize the main user interface"""
        self.setWindowTitle('Sudoku')  # Set window title
        self.setGeometry(100, 100, 600, 600)  # Set window geometry

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout setup
        self.main_layout = QVBoxLayout()

        # Difficulty selection setup
        self.difficulty_layout = QHBoxLayout()
        self.difficulty_label = QLabel('Select Difficulty: ')
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(['Easy', 'Medium', 'Hard'])
        self.difficulty_layout.addWidget(self.difficulty_label)
        self.difficulty_layout.addWidget(self.difficulty_combo)
        self.main_layout.addLayout(self.difficulty_layout)

        # Sudoku grid setup
        self.grid_layout = QGridLayout()
        self.cells = []
        for row in range(9):
            row_cells = []
            for col in range(9):
                cell = QLineEdit()
                cell.setFixedSize(40, 40)
                cell.setAlignment(Qt.AlignCenter)
                cell.setMaxLength(1)
                cell.setValidator(QIntValidator(1, 9))
                cell.textChanged.connect(self.check_input)  # Connect text changed signal to check_input function
                cell.setFont(QFont("Arial", 16))
                self.grid_layout.addWidget(cell, row, col)  # Add cell widget to grid layout
                row_cells.append(cell)
            self.cells.append(row_cells)
        self.main_layout.addLayout(self.grid_layout)

        # Buttons setup
        self.buttons_layout = QHBoxLayout()
        self.new_game_button = QPushButton('New Game')
        self.new_game_button.clicked.connect(self.new_game)  # Connect clicked signal to new_game function
        self.hint_button = QPushButton('Hint')
        self.hint_button.clicked.connect(self.hint)  # Connect clicked signal to hint function
        self.restart_button = QPushButton('Restart')
        self.restart_button.clicked.connect(self.restart)  # Connect clicked signal to restart function
        self.save_button = QPushButton('Save Game')
        self.save_button.clicked.connect(self.save_game)  # Connect clicked signal to save_game function
        self.load_button = QPushButton('Load Game')
        self.load_button.clicked.connect(self.load_game)  # Connect clicked signal to load_game function
        self.quit_button = QPushButton('Quit')
        self.quit_button.clicked.connect(self.quit)  # Connect clicked signal to quit function
        self.buttons_layout.addWidget(self.new_game_button)
        self.buttons_layout.addWidget(self.hint_button)
        self.buttons_layout.addWidget(self.restart_button)
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.load_button)
        self.buttons_layout.addWidget(self.quit_button)
        self.main_layout.addLayout(self.buttons_layout)

        self.central_widget.setLayout(self.main_layout)  # Set central widget layout

    def new_game(self):
        """Starts a new game"""
        difficulty = self.difficulty_combo.currentText()  # Get current selected difficulty
        self.game_data = self.generate_sudoku(difficulty)  # Generate Sudoku game data
        self.errors = 0  # Reset errors counter to 0
        self.update_grid()  # Update the UI grid with new game data

    def restart(self):
        """Restarts the current game"""
        if self.game_data:
            self.errors = 0  # Reset errors counter to 0
            self.update_grid()  # Update the UI grid with current game data

    def hint(self):
        """Provides a hint for the current game"""
        if self.game_data:
            empty_cells = [(r, c) for r in range(9) for c in range(9) if self.cells[r][c].text() == '']
            if empty_cells:
                r, c = random.choice(empty_cells)  # Choose a random empty cell
                self.cells[r][c].setText(str(self.game_data['solution'][r][c]))  # Set hint number in cell

    def save_game(self):
        """Saves the current game state to a file"""
        if self.game_data:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Game", "", "Sudoku Files (*.sudoku);;All Files (*)", options=options)
            if file_name:
                save_data = {
                    'puzzle': self.game_data['puzzle'].tolist(),  # Convert puzzle numpy array to list
                    'solution': self.game_data['solution'].tolist(),  # Convert solution numpy array to list
                    'grid': [[cell.text() for cell in row] for row in self.cells]  # Get text from each cell in grid
                }
                with open(file_name, 'w') as file:
                    json.dump(save_data, file)  # Write save_data to file in JSON format

    def load_game(self):
        """Loads a saved game state from a file"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Game", "", "Sudoku Files (*.sudoku);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                load_data = json.load(file)  # Load data from file using JSON
                self.game_data = {
                    'puzzle': np.array(load_data['puzzle']),  # Convert puzzle list to numpy array
                    'solution': np.array(load_data['solution'])  # Convert solution list to numpy array
                }
                for r, row in enumerate(load_data['grid']):
                    for c, value in enumerate(row):
                        self.cells[r][c].setText(value)  # Set text in each cell based on loaded data

    def quit(self):
        """Quits the application"""
        self.close()  # Close the main window

    def generate_sudoku(self, difficulty):
        """Generates a Sudoku puzzle based on difficulty"""
        # Generate a complete Sudoku solution
        solution = np.zeros((9, 9), dtype=int)
        self.fill_grid(solution)  # Fill the solution grid
        puzzle = solution.copy()
        if difficulty == 'Easy':
            self.remove_numbers(puzzle, 40)  # Remove numbers for easy difficulty
        elif difficulty == 'Medium':
            self.remove_numbers(puzzle, 50)  # Remove numbers for medium difficulty
        else:
            self.remove_numbers(puzzle, 60)  # Remove numbers for hard difficulty
        return {'puzzle': puzzle, 'solution': solution}  # Return puzzle and solution as dictionary

    def remove_numbers(self, grid, count):
        """Randomly removes numbers from the Sudoku puzzle"""
        attempts = 0
        max_attempts = 81 * 10
        while count > 0 and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if grid[row][col] != 0:
                backup = grid[row][col]
                grid[row][col] = 0
                grid_copy = grid.copy()
                if self.solve_grid(grid_copy):
                    count -= 1
                else:
                    grid[row][col] = backup
            attempts += 1

    def fill_grid(self, grid):
        """Recursively fills the Sudoku grid"""
        numbers = list(range(1, 10))
        for i in range(0, 81):
            row = i // 9
            col = i % 9
            if grid[row][col] == 0:
                random.shuffle(numbers)
                for number in numbers:
                    if self.is_safe(grid, row, col, number):
                        grid[row][col] = number
                        if self.find_empty_location(grid) is None:
                            return True
                        else:
                            if self.fill_grid(grid):
                                return True
                break
        grid[row][col] = 0
        return False

    def solve_grid(self, grid):
        """Recursively solves the Sudoku grid"""
        location = self.find_empty_location(grid)
        if not location:
            return True
        row, col = location
        for number in range(1, 10):
            if self.is_safe(grid, row, col, number):
                grid[row][col] = number
                if self.solve_grid(grid):
                    return True
                grid[row][col] = 0
        return False

    def is_safe(self, grid, row, col, number):
        """Checks if it's safe to place a number in a given position"""
        return (number not in grid[row] and
                number not in grid[:, col] and
                number not in grid[row - row % 3:row - row % 3 + 3, col - col % 3:col - col % 3 + 3])

    def find_empty_location(self, grid):
        """Finds the first empty location in the Sudoku grid"""
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return (i, j)
        return None

    def update_grid(self):
        for r in range(9):
            for c in range(9):
                if self.game_data['puzzle'][r][c] != 0:
                    self.cells[r][c].setText(str(self.game_data['puzzle'][r][c]))  # Set cell text from puzzle data
                    self.cells[r][c].setReadOnly(True)  # Set cell as read-only if it's pre-filled
                else:
                    self.cells[r][c].setText('')  # Clear cell text if it's empty
                    self.cells[r][c].setReadOnly(False)  # Set cell as editable if it's empty

    # Add visual separation between 3x3 blocks
        for r in range(9):
            for c in range(9):
                if (r % 3 == 0 and r != 0) or (c % 3 == 0 and c != 0):
                    if c % 3 == 0 and c != 0:
                        spacer = QWidget()
                        spacer.setFixedSize(4, 4)
                        self.grid_layout.addWidget(spacer, r, c)  # Add spacer widget to grid layout
                    if r % 3 == 0 and r != 0:
                        spacer = QWidget()
                        spacer.setFixedSize(4, 4)
                        self.grid_layout.addWidget(spacer, r, c)  # Add spacer widget to grid layout
                        
    def check_input(self):
        """Checks if the input in a cell is correct"""
        sender = self.sender()  # Get the sender object (QLineEdit)
        if not sender.text():  # If text is empty, return
            return
        row, col = None, None
        for r in range(9):
            for c in range(9):
                if self.cells[r][c] == sender:  # Find the cell corresponding to the sender
                    row, col = r, c
                    break
        if row is not None and col is not None:
            if int(sender.text()) != self.game_data['solution'][row][col]:
                self.errors += 1
                if self.errors >= 3:
                    QMessageBox.warning(self, 'Game Over', 'You have made 3 mistakes. Game over!')
                    self.new_game()  # Start a new game on game over
                else:
                    QMessageBox.warning(self, 'Incorrect', f'Incorrect number! Mistakes: {self.errors}/3')
                sender.clear()  # Clear incorrect input from cell
            else:
                if all(self.cells[r][c].text() for r in range(9) for c in range(9)):
                    QMessageBox.information(self, 'You Win!', 'Congratulations! You have completed the Sudoku.')  # Show win message

def main():
    """Main function to run the Sudoku game"""
    app = QApplication(sys.argv)
    game = SudokuGame()  # Create SudokuGame instance
    game.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application

if __name__ == '__main__':
    main()  # Run the main function if script is executed directly
