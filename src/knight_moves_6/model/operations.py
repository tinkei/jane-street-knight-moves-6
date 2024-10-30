from typing import Optional

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from knight_moves_6.model.model_abc import ABCCombination
from knight_moves_6.model.model_base import Base
from knight_moves_6.model.model_path import KnightPath
from knight_moves_6.model.model_score import PathScore
from knight_moves_6.model.model_solution import Solution


def add_abc_combination(session: Session, A: int, B: int, C: int, sum_abc: int) -> Optional[ABCCombination]:
    """
    Adds an ABCCombination to the database if it does not already exist.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        A (int): Value for A.
        B (int): Value for B.
        C (int): Value for C.
        sum_abc (int): Sum of A, B, and C.

    Returns:
        Optional[ABCCombination]: The ABCCombination instance if added, or None if it already exists.
    """
    combination = ABCCombination(A=A, B=B, C=C, sum_abc=sum_abc)
    stmt = insert(ABCCombination).values(A=A, B=B, C=C, sum_abc=sum_abc).on_conflict_do_nothing()
    session.execute(stmt)
    session.commit()
    return session.query(ABCCombination).filter_by(A=A, B=B, C=C).first()


def get_unevaluated_abc_combinations(session: Session) -> list[ABCCombination]:
    """
    Retrieves all unevaluated ABCCombination records from the database.

    Args:
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        list[ABCCombination]: List of unevaluated ABCCombination instances.
    """
    return session.query(ABCCombination).filter_by(evaluated=False).all()


def add_knight_path(session: Session, start: str, path: str, expression: str) -> Optional[KnightPath]:
    """
    Adds a KnightPath to the database if it does not already exist.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        start (str): Starting point of the path.
        path (str): Path as a string.
        expression (str): Mathematical expression for the path score.

    Returns:
        Optional[KnightPath]: The KnightPath instance if added, or None if it already exists.
    """
    stmt = insert(KnightPath).values(start=start, path=path, expression=expression).on_conflict_do_nothing()
    session.execute(stmt)
    session.commit()
    return session.query(KnightPath).filter_by(path=path, expression=expression).first()


def add_path_score(session: Session, abc_combination_id: int, knight_path_id: int, score: int) -> Optional[PathScore]:
    """
    Adds a PathScore to the database if it does not already exist.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        abc_combination_id (int): Foreign key ID of the associated ABCCombination.
        knight_path_id (int): Foreign key ID of the associated KnightPath.
        score (int): Calculated score for the path.

    Returns:
        Optional[PathScore]: The PathScore instance if added, or None if it already exists.
    """
    stmt = (
        insert(PathScore)
        .values(abc_combination_id=abc_combination_id, knight_path_id=knight_path_id, score=score)
        .on_conflict_do_nothing()
    )
    session.execute(stmt)
    session.commit()
    return (
        session.query(PathScore).filter_by(abc_combination_id=abc_combination_id, knight_path_id=knight_path_id).first()
    )


def get_path_scores(session: Session) -> list[PathScore]:
    """
    Retrieves all PathScore entries from the database.

    Args:
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        list[PathScore]: List of all PathScore instances.
    """
    return session.query(PathScore).all()


def add_solution(
    session: Session, A: int, B: int, C: int, path1: str, path2: str, score1: int, score2: int, sum_abc: int
) -> Optional[Solution]:
    """
    Adds a Solution entry to the database if it does not already exist.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        A (int): Value for A.
        B (int): Value for B.
        C (int): Value for C.
        path1 (str): First knight path as a string.
        path2 (str): Second knight path as a string.
        score1 (int): Score of the first path.
        score2 (int): Score of the second path.
        sum_abc (int): Sum of A, B, and C.

    Returns:
        Optional[Solution]: The Solution instance if added, or None if it already exists.
    """
    stmt = (
        insert(Solution)
        .values(A=A, B=B, C=C, path1=path1, path2=path2, score1=score1, score2=score2, sum_abc=sum_abc)
        .on_conflict_do_nothing()
    )
    session.execute(stmt)
    session.commit()
    return session.query(Solution).filter_by(A=A, B=B, C=C, path1=path1, path2=path2).first()


def get_top_solutions(session: Session, n: int) -> list[Solution]:
    """
    Retrieves the top N solutions sorted by sum_abc.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        n (int): Number of solutions to retrieve.

    Returns:
        list[Solution]: List of top N Solution instances sorted by sum_abc.
    """
    return session.query(Solution).order_by(Solution.sum_abc).limit(n).all()
