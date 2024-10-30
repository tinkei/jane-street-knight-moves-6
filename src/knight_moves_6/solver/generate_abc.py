import itertools

from knight_moves_6.calculation.validation import is_valid_abc
from knight_moves_6.model.database import ABCCombination, Session


def generate_all_abc_combinations(max_sum: int = 50) -> list[tuple[int, int, int, int]]:
    """Generate all possible combinations of ABC's.

    A, B, C are distinct positive integers and their sum is <= `max_sum` (default = 50).

    Args:
        max_sum (int): Maximum allowed sum of `A + B + C`. Default: 50.

    Returns:
        list[tuple[int, int, int, int]]: A list containing tuples of `(A + B + C, A, B, C)`.
    """
    combo_list = []
    for A, B, C in itertools.combinations(range(1, max_sum + 1), 3):
        if is_valid_abc(A, B, C, max_sum=max_sum):
            combo_list.append((A + B + C, A, B, C))
    combo_list.sort()
    print(f"{len(combo_list)} combinations of ABC generated.")
    return combo_list


# Example script to populate the database with A, B, C values if needed
def populate_combinations(max_sum: int = 50) -> list[tuple[int, int, int, int]]:
    """Generate only combinations of ABC's that are not already present in the database.

    A, B, C are distinct positive integers and their sum is <= `max_sum` (default = 50).

    Args:
        max_sum (int): Maximum allowed sum of `A + B + C`. Default: 50.

    Returns:
        list[tuple[int, int, int, int]]: A list containing tuples of `(A + B + C, A, B, C)`.
    """
    # TODO: Move DB operations to Model.
    session = Session()
    combo_list = []

    # Load existing combinations of ABC's to avoid duplicated efforts.
    existing_combinations = set(
        (combo.A, combo.B, combo.C) for combo in session.query(ABCCombination.A, ABCCombination.B, ABCCombination.C)
    )

    # Generate all unique combinations where A, B, C are distinct positive integers
    for A, B, C in itertools.combinations(range(1, max_sum + 1), 3):
        if (A, B, C) not in existing_combinations and is_valid_abc(A, B, C, max_sum=max_sum):
            combo_list.append((A + B + C, A, B, C))

    combo_list.sort()
    print(f"{len(combo_list)} combinations of ABC generated.")

    # Write to database.
    try:
        for sum_abc, A, B, C in combo_list:
            combo = ABCCombination(A=A, B=B, C=C, sum_abc=sum_abc)
            session.add(combo)
        session.commit()
    finally:
        session.close()

    return combo_list


if __name__ == "__main__":
    from collections import Counter

    from knight_moves_6.calculation.constant import MAX_SUM

    # Populate combinations if database is empty
    combo_list = populate_combinations(max_sum=MAX_SUM)

    # Waste compute to generate all 2972 combinations of A, B, C.
    # combo_list = generate_all_abc_combinations(max_sum=MAX_SUM)
    # Measure stats (number of combinations that sums to X):
    c = Counter([x[0] for x in combo_list])
    c2 = [(key, val) for key, val in c.items()]
    c2.sort()
    for key, val in c2:
        print(f"{val: 3d} combinations sum to {key}")
