import sqlalchemy as sql
from .db_session import DataBase


class IsPaying(DataBase):
    __tablename__ = 'payment_codes'

    number = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    id = sql.Column(sql.Integer, index=True, unique=False, nullable=False)
    code = sql.Column(sql.String, nullable=False, unique=False, index=True)