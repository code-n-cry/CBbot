import sqlalchemy as sql
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec

DataBase = dec.declarative_base()
__factory = None


def initialization():
    global __factory

    if __factory:
        return

    connection = f'postgresql://tveoirzaohoepo:a9e2e8cdbbaebebe5a5f18906c2015fc5a16389fcab2d1dda09ed6b4ecb7fe2f@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/d9beeg70n64ksh'
    engine = sql.create_engine(connection, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    DataBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
