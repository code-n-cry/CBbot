import sqlalchemy as sql
from sqlalchemy import orm
from .db_session import DataBase


class IsVerifying(DataBase):
    __tablename__ = 'codes'

    number = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    id = sql.Column(sql.Integer, nullable=False, index=True)
    code = sql.Column(sql.Integer, nullable=False, unique=False, index=True)

