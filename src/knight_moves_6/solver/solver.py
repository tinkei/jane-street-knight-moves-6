from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from time import sleep
from typing import Generator

from sqlalchemy import asc, insert, select, tuple_
from sqlalchemy.orm import Query

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


def generate_batches(session: Session, batch_size: int = 100000) -> Generator[list[KnightPath], None, None]:
    """
    Yields batches of knight paths from the database, ordered by id.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        batch_size (int): Number of knight paths in each batch.

    Yields:
        Generator[list[KnightPath], None, None]: Batch of knight paths of specified size.
    """
    query: Query = session.query(KnightPath).execution_options(stream_results=True).yield_per(batch_size)
    # .order_by(asc(KnightPath.id))
    knight_paths_batch = []
    for knight_path in query:
        knight_paths_batch.append(knight_path)
        if len(knight_paths_batch) == batch_size:
            yield knight_paths_batch  # Yield a full batch
            knight_paths_batch = []  # Reset for the next batch
    if knight_paths_batch:  # Yield any remaining rows after the loop completes
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

    # Need to evaluate twice somehow. The first `eval()` only substitutes the values of A, B, C.
    path_scores = [
        {
            "abc_combination_id": combination.id,
            "knight_path_id": path.id,
            "score": eval(eval(path.expression.format(A=A, B=B, C=C))),
        }
        for path in knight_paths
    ]
    # Store the evaluated score in PathScore table only when it is equal to 2024:
    path_scores = [path for path in path_scores if path["score"] == PATH_SUM]

    return path_scores


def insert_unique_path_scores(session: Session, path_scores: list[dict]) -> None:
    """Check for duplicates before insertion!"""
    # Extract unique constraints from the incoming data (e.g., by specific fields).
    unique_constraints = {(ps["abc_combination_id"], ps["knight_path_id"]) for ps in path_scores}
    print(f"Attempting to insert {len(path_scores)} records to `PathScore`.")

    # Query for existing records that match the unique constraints.
    existing_records = session.execute(
        select(PathScore.abc_combination_id, PathScore.knight_path_id).where(
            tuple_(PathScore.abc_combination_id, PathScore.knight_path_id).in_(unique_constraints)
        )
    ).all()
    print(f"Found {len(existing_records)} existing records in `PathScore`.")

    # Filter out duplicates from path_scores.
    existing_constraints = set(existing_records)
    unique_path_scores = [
        ps for ps in path_scores if (ps["abc_combination_id"], ps["knight_path_id"]) not in existing_constraints
    ]
    print(f"Inserting remaining {len(unique_path_scores)} new records to `PathScore`.")

    # Insert the filtered unique records.
    if unique_path_scores:
        session.bulk_insert_mappings(PathScore, unique_path_scores)
        session.commit()


def solver(session: Session, max_workers: int = 16, batch_size: int = 100000):
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
        jobs = []
        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for path_batch in generate_batches(session, batch_size=batch_size):
                jobs.append(executor.submit(evaluate_knight_paths_for_abc_combination, combination, path_batch))

            for job in as_completed(jobs):
                # Collect results as they complete.
                sleep(1)
                try:
                    path_scores = job.result()
                    # del jobs[job]
                except RuntimeError as e:
                    print(f"Error encountered: {e}")
                    continue
                # print(path_scores[0]["score"])
                # print(type(path_scores[0]["score"]))
                if len(path_scores) > 0:
                    print(f"{len(path_scores)} valid path detected!")
                    insert_unique_path_scores(session, path_scores)
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
