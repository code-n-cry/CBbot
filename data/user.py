import sqlalchemy as sql
from .db_session import DataBase


class User(DataBase):
    __tablename__ = 'accounts'

    id = sql.Column(sql.Integer, index=True, unique=True, nullable=False, primary_key=True)
    email = sql.Column(sql.String, nullable=False, unique=True)
    email_verified = sql.Column(sql.Boolean, nullable=False, default=True)
    bitcoin_wallet = sql.Column(sql.String, nullable=True, unique=False, default=None)
    litecoin_wallet = sql.Column(sql.String, nullable=True, unique=False, default=None)
    ethereum_wallet = sql.Column(sql.String, nullable=True, unique=False, default=None)
    dogecoin_wallet = sql.Column(sql.String, nullable=True, unique=False, default=None)
