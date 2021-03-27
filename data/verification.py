import sqlalchemy as sql
from .db_session import DataBase


class IsVerifying(DataBase):
    __tablename__ = 'codes'

    number = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    id = sql.Column(sql.Integer, index=True, unique=False)
    code = sql.Column(sql.Integer, nullable=False, unique=False, index=True)
