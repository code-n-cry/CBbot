import sqlalchemy as sql
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec
import os

DataBase = dec.declarative_base()
__factory = None


def initialization():
    global __factory

    if __factory:
        return

    connection = connection = str(os.getenv('DATABASE_URL')).replace('postgres', 'postgresql')
    engine = sql.create_engine(connection, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    DataBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
