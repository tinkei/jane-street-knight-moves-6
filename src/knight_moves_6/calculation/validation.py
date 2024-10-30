from knight_moves_6.calculation.calculate_score import calculate_path_score
from knight_moves_6.calculation.constant import KNIGHT_MOVES, PATH_SUM
from knight_moves_6.calculation.coordinate_map import coord_to_index, solution_string_to_coordinate_list


def is_valid_abc(A: int, B: int, C: int, max_sum: int = 50) -> bool:
    return A + B + C <= max_sum and A != B and B != C and C != A


def is_valid_a1_f6(path: list[str]) -> bool:
    return path[0] == "a1" and path[-1] == "f6"


def is_valid_a6_f1(path: list[str]) -> bool:
    return path[0] == "a6" and path[-1] == "f1"


def is_valid_start_end(path: list[str]) -> bool:
    return is_valid_a1_f6(path) or is_valid_a6_f1(path)


def is_within_bounds(row: int, col: int) -> bool:
    """Check if a move is within grid bounds."""
    return 0 <= row < 6 and 0 <= col < 6


def is_valid_move(row: int, col: int, visited: tuple[int, int]) -> bool:
    """Validate a move (ensure it hasn't been visited within the trip path)."""
    return is_within_bounds(row, col) and (row, col) not in visited


def knight_moves(row: int, col: int) -> list[tuple[int, int]]:
    """Generate all possible knight moves from a position within the bounds of the grid."""
    valid_moves = []
    # Possible knight moves (row change, col change).
    for dr, dc in KNIGHT_MOVES:
        new_row, new_col = row + dr, col + dc
        # Check if the move is within grid bounds (6x6 grid).
        if is_within_bounds(new_row, new_col):
            valid_moves.append((new_row, new_col))

    return valid_moves


def is_valid_path(path: list[str], start: str, end: str) -> bool:
    """
    Validate a sequence of moves as a knight path from start to end.

    Args:
        path (list of str): List of positions in coordinate format.
        start (str): Starting position in coordinate format, e.g., "a1".
        end (str): Ending position in coordinate format, e.g., "f6".

    Returns:
        bool: True if the path is valid, False otherwise.
    """
    # Ensure the path starts and ends correctly.
    if path[0] != start or path[-1] != end:
        return False

    # Initialize visited set to keep track of visited squares.
    visited = set()

    # Mark the starting position as visited.
    path_row_col = [coord_to_index(coord) for coord in path]
    visited.add(path_row_col[0])
    prev_row, prev_col = path_row_col[0]

    # Verify each move in the path.
    for i in range(1, len(path_row_col)):
        next_row, next_col = path_row_col[i]

        # Check if the move is a valid knight move and not revisited.
        if path_row_col[i] not in knight_moves(prev_row, prev_col) or path_row_col[i] in visited:
            return False

        # Mark as visited and move to the next position.
        visited.add(path_row_col[i])
        prev_row, prev_col = next_row, next_col

    return True


def is_valid_solution(grid: list[list[str]], solution_string: str) -> bool:
    A, B, C, path1, path2 = solution_string_to_coordinate_list(solution_string)
    return (
        is_valid_abc(A, B, C, 256)
        and is_valid_path(path1, "a1", "f6")
        and is_valid_path(path2, "a6", "f1")
        and is_valid_a1_f6(path1)
        and is_valid_a6_f1(path2)
        and calculate_path_score(grid, path1, A, B, C) == PATH_SUM
        and calculate_path_score(grid, path2, A, B, C) == PATH_SUM
    )


if __name__ == "__main__":

    from knight_moves_6.calculation.constant import GRID as grid
    from knight_moves_6.calculation.constant import SAMPLE_SOLUTION as solution_string

    # Testing with the example case provided.
    # Example format: "1,2,253,a1,b3,c5,d3,f4,d5,f6,a6,c5,a4,b2,c4,d2,f1"
    print(f"Is sample solution valid? {is_valid_solution(grid, solution_string)}")

    # Strip the values and extract the path for testing purposes.
    A, B, C, path1, path2 = solution_string_to_coordinate_list(solution_string)

    # Check if both paths are valid knight tours.
    print("Path 1 is valid:", is_valid_path(path1, "a1", "f6"))
    print("Path 2 is valid:", is_valid_path(path2, "a6", "f1"))
    print("Path 1 has valid start-end:", is_valid_start_end(path1))
    print("Path 2 has valid start-end:", is_valid_start_end(path2))

    test_path = "a1,b3,c5,d3,e5,c4,b2,a4,c3,e2,f4,e6,d4,c6,b4,c2,e1,f3,d2,b1,a3,b5,d6,e4,f2,d1,e3,d5,f6"
    test_path = test_path.split(",")
    print(test_path)
    print(len(test_path) == len(set(test_path)))
    print("Test path is valid:", is_valid_path(test_path, "a1", "f6"))
    print("Test path has valid start-end:", is_valid_start_end(test_path))
