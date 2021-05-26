import sqlalchemy as sql
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec

DataBase = dec.declarative_base()
__factory = None


def initialization():
    global __factory

    if __factory:
        return

    connection = f'postgresql://jmbwrqtkciptar:49a7cc52b929258ba0667f13e3227601473c1245ef78dd5965ced615442a1dc0@ec2-52-214-178-113.eu-west-1.compute.amazonaws.com:5432/d3vhsjgllvb4ht'
    engine = sql.create_engine(connection, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    DataBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
