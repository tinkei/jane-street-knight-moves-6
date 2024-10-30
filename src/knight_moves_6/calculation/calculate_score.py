from knight_moves_6.calculation.constant import GRID
from knight_moves_6.calculation.coordinate_map import coord_to_index


def calculate_path_score(grid: list[list[str]], path: list[str], A: int, B: int, C: int) -> int:
    """
    Calculate the score of a given knight path.

    Args:
        grid (list of list of str): 2D grid with "A", "B", "C" as string values in each cell.
        path (list of str): List of positions in coordinate format (e.g., "a1", "b3").
        A (int): The positive integer value for "A" in the grid.
        B (int): The positive integer value for "B" in the grid.
        C (int): The positive integer value for "C" in the grid.

    Returns:
        int: The final score of the path.
    """
    # Define a dictionary to map "A", "B", "C" to their integer values.
    symbol_map = {"A": A, "B": B, "C": C}

    # Start with the initial score based on the first square's value
    path_row_col = [coord_to_index(coord) for coord in path]
    row, col = path_row_col[0]
    prev_symbol: str = grid[row][col]
    score = symbol_map[prev_symbol]

    # Iterate through the path, starting from the second position
    for i in range(1, len(path)):
        # Get the row and column of the next position
        row, col = path_row_col[i]
        curr_symbol: str = grid[row][col]

        # Calculate score based on the rules
        if curr_symbol == prev_symbol:
            # Same value, add the value to the score
            score += symbol_map[curr_symbol]
        else:
            # Different value, multiply the score by the value
            score *= symbol_map[curr_symbol]

        # Update current value to the new square's value
        prev_symbol = curr_symbol

    return score


def calculate_path_score_marginal(grid: list[list[str]], path: list[str], A: int, B: int, C: int) -> list[int]:
    """
    Calculate the marginal score increase at each step in the path.

    Args:
        grid (list of list of str): 2D grid with "A", "B", "C" as string values in each cell.
        path (list of str): List of positions in coordinate format (e.g., "a1", "b3").
        A (int): The positive integer value for "A" in the grid.
        B (int): The positive integer value for "B" in the grid.
        C (int): The positive integer value for "C" in the grid.

    Returns:
        list: Incremental score increase at each step.
    """
    # Define a dictionary to map "A", "B", "C" to their integer values.
    symbol_map = {"A": A, "B": B, "C": C}

    marginal_scores = []
    path_row_col = [coord_to_index(coord) for coord in path]
    row, col = path_row_col[0]
    prev_symbol = grid[row][col]
    score = symbol_map[prev_symbol]
    marginal_scores.append(score)

    for i in range(1, len(path_row_col)):
        row, col = path_row_col[i]
        curr_symbol = grid[row][col]

        if curr_symbol == prev_symbol:
            score_change = symbol_map[curr_symbol]
            score += symbol_map[curr_symbol]
        else:
            score_change = score * symbol_map[curr_symbol] - score
            score *= symbol_map[curr_symbol]

        prev_symbol = curr_symbol
        marginal_scores.append(score_change)

    return marginal_scores


def calculate_path_score_cumulative(grid: list[list[str]], path: list[str], A: int, B: int, C: int) -> list[int]:
    """
    Calculate the cumulative score at each step in the path.

    Args:
        grid (list of list of str): 2D grid with "A", "B", "C" as string values in each cell.
        path (list of str): List of positions in coordinate format (e.g., "a1", "b3").
        A (int): The positive integer value for "A" in the grid.
        B (int): The positive integer value for "B" in the grid.
        C (int): The positive integer value for "C" in the grid.

    Returns:
        list: Cumulative score at each step.
    """
    # Define a dictionary to map "A", "B", "C" to their integer values.
    symbol_map = {"A": A, "B": B, "C": C}

    cumulative_scores = []
    path_row_col = [coord_to_index(coord) for coord in path]
    row, col = path_row_col[0]

    prev_symbol = grid[row][col]
    score = symbol_map[prev_symbol]
    cumulative_scores.append(score)

    for i in range(1, len(path_row_col)):
        row, col = path_row_col[i]
        curr_symbol = grid[row][col]

        if curr_symbol == prev_symbol:
            score += symbol_map[curr_symbol]
        else:
            score *= symbol_map[curr_symbol]

        cumulative_scores.append(score)
        prev_symbol = curr_symbol

    return cumulative_scores


def calculate_path_expression(grid: list[list[str]], path: list[str]) -> str:
    """
    Generates an f-string that represents the score calculation for a path based on knight moves.

    Args:
        path (list of str): List of positions in coordinate format (e.g., "a1", "b3").
        A (int): The positive integer value for "A" in the grid.
        B (int): The positive integer value for "B" in the grid.
        C (int): The positive integer value for "C" in the grid.

    Returns:
        str: f-string representing the sequence of mathematical operations.
    """
    path_row_col = [coord_to_index(coord) for coord in path]
    row, col = path_row_col[0]
    prev_symbol = grid[row][col]
    expression = ""

    # Loop over the path to build the expression
    for i in range(1, len(path)):
        # Convert position to row and col
        row, col = path_row_col[i]
        curr_symbol = grid[row][col]

        # Initialize the expression starting with A, the starting value of the path.
        if i == 1:
            expression = f"{{{prev_symbol}}}"

        # Add multiplication or addition operation based on the transition rule.
        if prev_symbol == curr_symbol:
            # Same cell value, add.
            expression += f"+{{{curr_symbol}}}"
        else:
            # Different cell value, multiply.
            expression = f"({expression})*{{{curr_symbol}}}"

        prev_symbol = curr_symbol

    return f'f"{expression}"'


if __name__ == "__main__":

    # Example parameters
    A, B, C = 1, 2, 253  # Example values for A, B, and C
    example_path_1 = ["a1", "b3", "c5", "d3", "f4", "d5", "f6"]
    example_path_2 = ["a6", "c5", "a4", "b2", "c4", "d2", "f1"]

    # Calculate scores
    score1 = calculate_path_score(GRID, example_path_1, A, B, C)
    score2 = calculate_path_score(GRID, example_path_2, A, B, C)

    print("Score for path 1:", score1)
    print("Score for path 2:", score2)
    print(score1 == 2024)
    print(score2 == 2024)

    score1_cum = calculate_path_score_cumulative(GRID, example_path_1, A, B, C)
    score2_cum = calculate_path_score_cumulative(GRID, example_path_2, A, B, C)

    print("Cumulative score for path 1:", score1_cum)
    print("Cumulative score for path 2:", score2_cum)
    print(score1_cum[-1] == 2024)
    print(score2_cum[-1] == 2024)

    score1_mar = calculate_path_score_marginal(GRID, example_path_1, A, B, C)
    score2_mar = calculate_path_score_marginal(GRID, example_path_2, A, B, C)

    print("Marginal score for path 1:", score1_mar, "Sum:", sum(score1_mar))
    print("Marginal score for path 2:", score2_mar, "Sum:", sum(score2_mar))
    print(sum(score1_mar) == 2024)
    print(sum(score2_mar) == 2024)

    expression_template1 = calculate_path_expression(GRID, example_path_1)
    expression_template2 = calculate_path_expression(GRID, example_path_2)
    print(expression_template1)  # Output: f"(({A}+{A})*{B}+{B})*{C}+{C}+{C}"
    print(expression_template2)  # Output: f"(((({A})*{B})*{A}+{A})*{B}+{B})*{C}"
    A, B, C = 1, 2, 253
    expression_substituted1 = eval(expression_template1)
    expression_substituted2 = eval(expression_template2)
    print(expression_substituted1)
    print(expression_substituted2)
    # This would compute the score based on the generated formula.
    score1_exp = eval(expression_substituted1)
    score2_exp = eval(expression_substituted2)
    print(score1_exp)
    print(score2_exp)
    print(score1_exp == 2024)
    print(score2_exp == 2024)

    A, B, C = 2, 3, 1
    test_path = "a1,b3,c5,d3,e5,c4,b2,a4,c3,e2,f4,e6,d4,c6,b4,c2,e1,f3,d2,b1,a3,b5,d6,e4,f2,d1,e3,d5,f6"
    test_path = test_path.split(",")
    expression_template1 = calculate_path_expression(GRID, test_path)
    print(expression_template1)
    expression_substituted1 = eval(expression_template1)
    print(expression_substituted1)
    score1_exp = eval(expression_substituted1)
    print(score1_exp)
    print(score1_exp == 2024)
