# Mapping from coordinate notation to 2D indices and vice versa.
# Note that the coordinates are formatted in ("col", "row"), while the indices are (row, col).
def coord_to_index(coord: str) -> tuple[int, int]:
    """
    Converts coordinate format to 2D list indices.

    Args:
        coord (str): Coordinate string, like "a1" or "b3".

    Returns:
        tuple: Row and column indices as (row, col).
    """
    col = ord(coord[0]) - ord("a")  # "a" corresponds to column 0
    row = int(coord[1]) - 1
    return row, col


def index_to_coord(row: int, col: int) -> str:
    """
    Converts 2D list indices to coordinate format.

    Args:
        row (int): Row index (0-based).
        col (int): Column index (0-based).

    Returns:
        str: Coordinate string, like "a1" or "b3".
    """
    letter = chr(ord("a") + col)  # "a" + column index gives the correct letter
    number = str(row + 1)
    return letter + number


def solution_string_to_coordinate_list(solution_string: str) -> tuple[str, str, str, list[str], list[str]]:
    """
    Breaks down a solution string to individual components.

    Args:
        solution_string (str): A correctly formatted solution string.
            E.g. "1,2,253,a1,b3,c5,d3,f4,d5,f6,a6,c5,a4,b2,c4,d2,f1".

    Returns:
        tuple: A, B, C, and the two paths, with coordinates like "a1" or "b3".
    """
    solution_split = solution_string.split(",")
    A = solution_split[0]
    B = solution_split[1]
    C = solution_split[2]
    paths = solution_split[3:]
    path_start = paths.index("a6")
    path1 = paths[:path_start]
    path2 = paths[path_start:]
    return A, B, C, path1, path2


def path_to_solution_string(A, B, C, path1, path2) -> str:
    """
    Format a solution string from individual components.

    Args:
        tuple: A, B, C, and the two paths, with coordinates like "a1" or "b3".

    Returns:
        solution_string (str): A correctly formatted solution string.
            E.g. "1,2,253,a1,b3,c5,d3,f4,d5,f6,a6,c5,a4,b2,c4,d2,f1".
    """
    return ",".join((A, B, C, ",".join(path1), ",".join(path2)))


if __name__ == "__main__":

    from knight_moves_6.calculation.constant import SAMPLE_SOLUTION

    # Test construction and reconstruction of solution string.
    solution_string = SAMPLE_SOLUTION
    A, B, C, path1, path2 = solution_string_to_coordinate_list(solution_string)
    solution_string_test = path_to_solution_string(A, B, C, path1, path2)
    print(solution_string)
    print(solution_string_test)
    print(solution_string == solution_string_test)

    # Test coordinate mapping to and from list indices.
    print(path1)
    print(path2)
    path1_indices = [coord_to_index(node) for node in path1]
    path2_indices = [coord_to_index(node) for node in path2]
    print(path1_indices)
    print(path2_indices)
    path1_coor = [index_to_coord(*node) for node in path1_indices]
    path2_coor = [index_to_coord(*node) for node in path2_indices]
    print(path1_coor)
    print(path2_coor)
    print(path1 == path1_coor)
    print(path2 == path2_coor)
