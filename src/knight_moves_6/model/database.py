from sqlalchemy import asc, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from knight_moves_6.calculation.calculate_score import calculate_path_score
from knight_moves_6.calculation.constant import GRID
from knight_moves_6.calculation.coordinate_map import path_to_string, solution_string_to_coordinate_list, string_to_path
from knight_moves_6.model.model_abc import ABCCombination
from knight_moves_6.model.model_base import Base
from knight_moves_6.model.model_path import KnightPath
from knight_moves_6.model.model_solution import Solution


# Database setup: create a SQLite database in the local directory
def setup_database(db_name="knight-moves-6.db"):
    """Create an SQLite engine and setup the database."""
    engine = create_engine(f"sqlite:///{db_name}", echo=False)
    Base.metadata.create_all(engine)  # Create tables based on the model
    return engine


# Create a session factory
engine = setup_database()
Session = sessionmaker(bind=engine)


def write_solution(solution_string: str) -> None:
    """Write a solution to the database."""
    A, B, C, path1, path2 = solution_string_to_coordinate_list(solution_string)
    sum_abc = A + B + C
    score1 = calculate_path_score(GRID, path1, A, B, C)
    score2 = calculate_path_score(GRID, path2, A, B, C)
    solution = Solution(
        A=A,
        B=B,
        C=C,
        path1=path_to_string(path1),
        path2=path_to_string(path2),
        score1=score1,
        score2=score2,
        sum_abc=sum_abc,
    )
    session = Session()
    session.add(solution)
    session.commit()
    session.close()


def read_solutions() -> list[Solution]:
    """Read all solutions from the database."""
    session = Session()
    solutions = session.query(Solution).order_by(asc(Solution.sum_abc)).all()
    session.close()
    return solutions


def top_n(n: int) -> list[Solution]:
    """Get top N solutions with score = 2024, and sorted by `sum_abc`."""
    session = Session()
    top_solutions = (
        session.query(Solution)
        .filter(Solution.score1 == 2024)
        .filter(Solution.score2 == 2024)
        .order_by(asc(Solution.sum_abc))
        .limit(n)
        .all()
    )
    session.close()
    return top_solutions


def read_abc(only_unevaluated: bool = True) -> list[ABCCombination]:
    session = Session()
    if only_unevaluated:
        abc_combinations = (
            session.query(ABCCombination)
            .filter(not ABCCombination.evaluated)
            .order_by(asc(ABCCombination.sum_abc))
            .all()
        )
    else:
        abc_combinations = session.query(ABCCombination).order_by(asc(ABCCombination.sum_abc)).all()
    session.close()
    return abc_combinations


if __name__ == "__main__":

    from knight_moves_6.calculation.constant import SAMPLE_SOLUTION as solution_string

    # Read all ABC combinations.
    abc_combinations = read_abc(only_unevaluated=False)
    print(f"Retrieved {len(abc_combinations)} combinations of ABC.")

    # Write example solution to database.
    try:
        write_solution(solution_string)
    except IntegrityError as e:
        print("Solution is already present in the DB. Moving on.")

    # Fetch and display all solutions.
    # all_solutions = read_solutions()
    # print("\nAll Solutions:")
    # for sol in all_solutions:
    #     print(
    #         f"A={sol.A}, B={sol.B}, C={sol.C}, path1={string_to_path(sol.path1)}, score1={sol.score1}, path2={string_to_path(sol.path2)}, score2={sol.score2}, sum_abc={sol.sum_abc}"
    #     )

    # Fetch and display top N solutions, as determined by `sum_abc`.
    top_solutions = top_n(5)
    print("\nTop N Solutions:")
    for sol in top_solutions:
        print(
            f"A={sol.A}, B={sol.B}, C={sol.C}, path1={string_to_path(sol.path1)}, score1={sol.score1}, path2={string_to_path(sol.path2)}, score2={sol.score2}, sum_abc={sol.sum_abc}"
        )
