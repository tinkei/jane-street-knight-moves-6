from sqlalchemy import Column, Integer, String, UniqueConstraint

from knight_moves_6.model.model_base import Base


# Define the Solution model to map to the database table
class Solution(Base):
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True)
    A = Column(Integer, nullable=False)
    B = Column(Integer, nullable=False)
    C = Column(Integer, nullable=False)
    path1 = Column(String, nullable=False)
    path2 = Column(String, nullable=False)
    score1 = Column(Integer, nullable=False)
    score2 = Column(Integer, nullable=False)
    sum_abc = Column(Integer, nullable=False)

    # Enforce uniqueness on the combination of A, B, C, path1, path2.
    __table_args__ = (UniqueConstraint("A", "B", "C", "path1", "path2", name="_a_b_c_path1_path2_uc"),)
