from sqlalchemy import Column, Integer, String, UniqueConstraint

from knight_moves_6.model.model_base import Base


class KnightPath(Base):
    __tablename__ = "knight_paths"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    expression = Column(String, nullable=True)

    # Enforce uniqueness on the combination of path and expression.
    __table_args__ = (UniqueConstraint("path", "expression", name="_path_expression_uc"),)
