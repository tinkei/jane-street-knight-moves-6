from knight_moves_6.calculation.calculate_score import calculate_path_expression
from knight_moves_6.calculation.constant import GRID, KNIGHT_MOVES
from knight_moves_6.calculation.coordinate_map import coord_to_index, index_to_coord, path_to_string
from knight_moves_6.calculation.validation import is_valid_move
from knight_moves_6.model.database import KnightPath, Session

# path1 = ["a1", "b3", "c5", "d3", "f4", "d5", "f6"]
# path2 = ["a6", "c5", "a4", "b2", "c4", "d2", "f1"]


def find_knight_paths(
    start: tuple[int, int],
    end: tuple[int, int],
    visited: set[tuple[int, int]],
    path: list[str],
    all_paths: list[list[str]],
    counter: list[int],
    batch_size: int = 200000,
) -> None:
    """
    Recursive function to find all valid paths from start to end without overlapping.
    """
    if start == end:
        all_paths.append(list(path))
        if len(all_paths) % batch_size == 0:
            counter[0] += len(all_paths)
            print(f"{batch_size}x paths identified! Total: {counter[0]} Current: {path_to_string(path)}")
            # Write paths to DB already and clear memory.
            write_knight_paths_to_db(all_paths)
            all_paths.clear()
        return

    # Debug interrupt. Default to 20M paths.
    # ~16GB memory use without batching, x2 for starting points "a1" and "a6".
    # 21.5GB of disk storage considering both starting points "a1" and "a6".
    if counter[0] >= 2e7:
        return

    row, col = start
    for dr, dc in KNIGHT_MOVES:
        new_row, new_col = row + dr, col + dc
        if is_valid_move(new_row, new_col, visited):
            visited.add((new_row, new_col))
            path.append(index_to_coord(new_row, new_col))
            find_knight_paths(
                start=(new_row, new_col), end=end, visited=visited, path=path, all_paths=all_paths, counter=counter
            )
            path.pop()
            visited.remove((new_row, new_col))


def write_knight_paths_to_db(knight_paths: list[str]):

    # Store paths in the database.
    session = Session()
    expressions = []
    try:
        for path in knight_paths:
            expression = calculate_path_expression(GRID, path)
            # print(path_to_string(path), expression)
            path_entry = KnightPath(start=path[0], path=path_to_string(path), expression=expression)
            expressions.append(expression)
            session.add(path_entry)
        session.commit()
    finally:
        session.close()


def generate_and_store_paths_a1() -> list[list[str]]:
    """Generate and store all corner-to-corner a1-f6 knight paths."""

    # Define start and end points for both required paths.
    a1_f6_start = coord_to_index("a1")
    a1_f6_end = coord_to_index("f6")
    a6_f1_start = coord_to_index("a6")
    a6_f1_end = coord_to_index("f1")

    all_paths = []
    counter = [0]

    # Find paths from a1 to f6.
    find_knight_paths(
        start=a1_f6_start,
        end=a1_f6_end,
        visited={a1_f6_start},
        path=[index_to_coord(*a1_f6_start)],
        all_paths=all_paths,
        counter=counter,
    )

    print(f"Identified {len(all_paths)} paths.")

    write_knight_paths_to_db(all_paths)

    # print(f"Identified {len(set(all_paths))} unique paths.")
    # print(f"Identified {len(set(expressions))} unique expressions.")
    return all_paths


def generate_and_store_paths_a6() -> list[list[str]]:
    """Generate and store all corner-to-corner a6-f1 knight paths."""

    # Define start and end points for both required paths.
    a1_f6_start = coord_to_index("a1")
    a1_f6_end = coord_to_index("f6")
    a6_f1_start = coord_to_index("a6")
    a6_f1_end = coord_to_index("f1")

    all_paths = []
    counter = [0]

    # Find paths from a6 to f1.
    find_knight_paths(
        start=a6_f1_start,
        end=a6_f1_end,
        visited={a6_f1_start},
        path=[index_to_coord(*a6_f1_start)],
        all_paths=all_paths,
        counter=counter,
    )

    print(f"Identified {len(all_paths)} paths.")

    write_knight_paths_to_db(all_paths)

    # print(f"Identified {len(set(all_paths))} unique paths.")
    # print(f"Identified {len(set(expressions))} unique expressions.")
    return all_paths


# Check results
def read_paths():
    session = Session()
    paths = session.query(KnightPath).all()
    for path in paths:
        print(path.path)
    session.close()


if __name__ == "__main__":

    # Run the path generation and storage process
    # all_paths = generate_and_store_paths_a1()
    # print(f"Identified {len(all_paths)} paths.")
    # all_paths = generate_and_store_paths_a6()
    # print(f"Identified {len(all_paths)} paths.")

    # Uncomment to test read_paths
    # read_paths()
    pass
