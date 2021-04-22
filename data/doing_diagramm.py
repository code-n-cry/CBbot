import sqlalchemy as sql
from sqlalchemy import orm
from .db_session import DataBase


class DoingDiagram(DataBase):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'diagram'

    id = sql.Column(sql.Integer, primary_key=True, index=True, unique=False, nullable=False)
    chosen_crypto = sql.Column(sql.String, index=False, unique=False, nullable=True)
    chosen_fiat = sql.Column(sql.String, index=False, unique=False, nullable=True)