import sqlalchemy as sql
import sqlalchemy.orm as orm
import logging
import sqlalchemy.ext.declarative as dec

DataBase = dec.declarative_base()
__factory = None


def initialization(filename: str):
    global __factory

    if __factory:
        return
    if not filename:
        return

    connection = f'sqlite:///{filename.strip()}?check_same_thread=False'
    engine = sql.create_engine(connection, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    DataBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
