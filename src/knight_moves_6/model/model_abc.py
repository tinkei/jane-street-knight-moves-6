from sqlalchemy import Boolean, Column, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from knight_moves_6.model.model_base import Base


# Define A, B, C combination model
class ABCCombination(Base):
    __tablename__ = "abc_combinations"

    id = Column(Integer, primary_key=True)
    A = Column(Integer, nullable=False)
    B = Column(Integer, nullable=False)
    C = Column(Integer, nullable=False)
    sum_abc = Column(Integer, nullable=False)
    evaluated = Column(Boolean, default=False)

    # Enforce uniqueness on the combination of A, B, C.
    __table_args__ = (UniqueConstraint("A", "B", "C", name="_a_b_c_uc"),)

    # Relationship to PathScore
    path_scores = relationship("PathScore", back_populates="abc_combination")
