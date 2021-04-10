import sqlalchemy as sql
from sqlalchemy import orm
from .db_session import DataBase


class IsPaying(DataBase):
    __tablename__ = 'payment_codes'

    number = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    id = sql.Column(sql.Integer, sql.ForeignKey('accounts.id'), index=True, unique=False,
                    nullable=False)
    code = sql.Column(sql.String, nullable=False, unique=True, index=True)
    crypto_currency_name = sql.Column(sql.String, nullable=False, unique=False,
                                      index=False)  # чтобы помнить, какая именно криптовалюта нужна пользователю
    user = orm.relation('User')
