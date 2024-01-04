from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

class Base(DeclarativeBase):
    pass

#Tabla de users de la aplicación
class Users(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, password={self.password!r})"
    
from sqlalchemy import create_engine
engine = create_engine("sqlite:///./database.db", echo=True)

Base.metadata.create_all(engine)



def add_user(name, password):
    """
    Add a user to the database with the given name and password.
    """
    with Session(engine) as session:
        user = Users(name=name, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user is not None
def check_user(name):
    """
    Check if the user exists in the database with the given name.

	"""
    #Check the user
    session = Session(engine)
    user = session.query(Users).filter_by(name=name).first()
    session.close()

    return user is not None

def check_user_and_password(name, password):
    """
    Check if the user exists and the password is correct in the database with the given name and password.

    """
    #Check the user and password
    session = Session(engine)
    user = session.query(Users).filter_by(name=name, password=password).first()
    session.close()

    return user is not None