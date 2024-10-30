from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Generator

from sqlalchemy import asc, insert

from knight_moves_6.calculation.calculate_score import calculate_path_score
from knight_moves_6.calculation.constant import PATH_SUM
from knight_moves_6.model.database import ABCCombination, Session, top_n
from knight_moves_6.model.model_abc import ABCCombination
from knight_moves_6.model.model_base import Base
from knight_moves_6.model.model_path import KnightPath
from knight_moves_6.model.model_score import PathScore
from knight_moves_6.model.model_solution import Solution


def abc_combination_generator(session: Session) -> Generator[ABCCombination, None, None]:
    """
    Generator that yields unevaluated A, B, C combinations entries from the database.

    Args:
        session (Session): SQLAlchemy session to interact with the database.

    Yields:
        ABCCombination: Unevaluated ABCCombination instances.
    """
    unevaluated_combinations = (
        session.query(ABCCombination).filter_by(evaluated=False).order_by(asc(ABCCombination.sum_abc)).all()
    )
    for combination in unevaluated_combinations:
        yield combination


def generate_batches(session: Session, batch_size: int = 1000) -> Generator[list[KnightPath], None, None]:
    """
    Yields batches of knight paths from the database, ordered by id.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        batch_size (int): Number of knight paths in each batch.

    Yields:
        Generator[list[KnightPath], None, None]: Batch of knight paths of specified size.
    """
    offset = 0
    while True:
        knight_paths_batch = (
            session.query(KnightPath).order_by(asc(KnightPath.id)).limit(batch_size).offset(offset).all()
        )
        if not knight_paths_batch:
            break  # Stop if no more paths are fetched.
        offset += batch_size
        yield knight_paths_batch


def evaluate_knight_paths_for_abc_combination(
    combination: ABCCombination, knight_paths: list[KnightPath]
) -> list[dict]:
    """
    Evaluate a batch of knight paths for a given ABCCombination and prepare results for batch insertion.

    Args:
        combination (ABCCombination): The ABCCombination instance.
        knight_paths_batch (List[KnightPath]): List of knight paths in the current batch.

    Returns:
        list[dict]: List of dicts containing path scores ready for bulk insert.
    """
    A, B, C = combination.A, combination.B, combination.C

    # Need to evaluate twice somehow. # The first `eval()` only substitutes the values of A, B, C.
    path_scores = [
        {
            "abc_combination_id": combination.id,
            "knight_path_id": path.id,
            "score": eval(eval(path.expression.format(A=A, B=B, C=C))),
        }
        for path in knight_paths
    ]
    # Store the evaluated score in PathScore table only when it is equal to 2024:
    path_scores = [path for path in knight_paths if path["score"] == PATH_SUM]

    return path_scores


def solver(session: Session, max_workers: int = 4, batch_size: int = 1000):
    """
    Main solver function that evaluates ABC combinations across batches of knight paths in parallel.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        max_workers (int): Maximum number of threads for parallel processing.
        batch_size (int): Batch size for knight paths.
    """
    all_scores = []

    for combination in abc_combination_generator(session):
        print(f"Processing A+B+C={combination.sum_abc} (A={combination.A} B={combination.B} C={combination.C})...")
        futures = []
        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for path_batch in generate_batches(session, batch_size=batch_size):
                futures.append(executor.submit(evaluate_knight_paths_for_abc_combination, combination, path_batch))

            for future in as_completed(futures):
                # Collect results as they complete.
                path_scores = future.result()
                # print(path_scores[0]["score"])
                # print(type(path_scores[0]["score"]))

                stmt = insert(PathScore).values(path_scores)  # .on_conflict_do_nothing()
                session.execute(stmt)
                session.commit()
                all_scores.extend([my_dict["score"] for my_dict in path_scores])

        # Commit the session to apply batched insertions after each combination.
        session.commit()
        # Update score and status in the database.
        session.query(ABCCombination).filter(ABCCombination.id == combination.id).update(
            {ABCCombination.evaluated: True}
        )
        session.commit()
        # break
        print(f"Processed A+B+C={combination.sum_abc} (A={combination.A} B={combination.B} C={combination.C}).")

    print("All combinations evaluated.")
    return all_scores


# Run the optimization
if __name__ == "__main__":
    # Define a test path as an example (replace this with actual path data)
    path = "a1,b3,c5,d3,f4,d5,f6,a6,c5,a4,b2,c4,d2,f1"

    # Start the optimization process
    session = Session()
    try:
        all_scores = solver(session)
        print(f"Number of valid combinations: {len(all_scores)}")
        print(f"Min score: {min(all_scores)}")
        print(f"Max score: {max(all_scores)}")
        print(f"Mean score: {sum(all_scores) / len(all_scores):.2f}")
        print(f"Number of scores that equals 2024: {len([score for score in all_scores if score == PATH_SUM])}")
        print("Done!")
    finally:
        session.close()

    # Check top solutions in the database
    print("Top solutions:")
    for solution in top_n(6):
        print(f"A={solution.A}, B={solution.B}, C={solution.C}, Score={solution.score}")
