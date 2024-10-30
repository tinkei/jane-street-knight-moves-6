from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from knight_moves_6.model.model_abc import ABCCombination
from knight_moves_6.model.model_base import Base
from knight_moves_6.model.model_path import KnightPath


class PathScore(Base):
    __tablename__ = "path_scores"

    id = Column(Integer, primary_key=True)
    abc_combination_id = Column(Integer, ForeignKey("abc_combinations.id"), nullable=False)
    knight_path_id = Column(Integer, ForeignKey("knight_paths.id"), nullable=False)
    score = Column(Integer, nullable=False)

    # Enforce uniqueness on the combination of abc_combination_id and knight_path_id
    __table_args__ = (UniqueConstraint("abc_combination_id", "knight_path_id", name="_abc_knight_uc"),)

    # Relationships to the other tables
    abc_combination = relationship("ABCCombination", back_populates="path_scores")
    knight_path = relationship("KnightPath", back_populates="path_scores")
