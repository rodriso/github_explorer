from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Column, Integer, String, ForeignKey,select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
import requests
import token_github
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
class Base(DeclarativeBase):
    pass

#Tabla de users de la aplicación
class Users(Base):
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)
    
    # Define the relationship with the "repository" table
    repositorys = relationship(
        "repository", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, password={self.password!r})"

class repository(Base):
    __tablename__ = "repositorys"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(String)  # Agregamos el dueño
    forks = Column(Integer)  # Agregamos el número de forks
    stars = Column(Integer)  # Agregamos el número de estrellas
    default_branch = Column(String)  # Agregamos la rama por defecto
    open_issues = Column(Integer)  # Agregamos el número de open issues
    creation_date = Column(DateTime)  # Agregamos la fecha de creación
    github_link = Column(String)  # Agregamos el enlace a la página del repositorio en GitHub

    # Define la relación con la tabla "Users" y la clave foránea
    user_id = Column(Integer, ForeignKey("user_account.id"))
    user = relationship("Users", back_populates="repositorys")  

    def __repr__(self):
        return f"Repository(id={self.id!r}, name={self.name!r}, owner={self.owner!r}, forks={self.forks!r}, stars={self.stars!r}, default_branch={self.default_branch!r}, open_issues={self.open_issues!r}, creation_date={self.creation_date!r}, github_link={self.github_link!r})"
    
from sqlalchemy import create_engine
engine = create_engine("sqlite:///./database.db", echo=True)


# Create tables with the updated schema
Base.metadata.create_all(engine)




def get_repo(user_id: int):
    with Session(engine) as session:
        user = session.query(Users).get(user_id)
        if user:
            return user.repositorys
        else:
            return []
    
from sqlalchemy.exc import IntegrityError

def add_repository(repo_name: str, user_id: int) -> int:
    # GitHub API endpoint para obtener información del repositorio
    api_url = f"https://api.github.com/repos/{repo_name}"

    try:
        with Session(engine) as session:
            # Hacer una solicitud GET a la API de GitHub con el encabezado de Autorización
            response = requests.get(api_url, headers={"Authorization": f"token {token_github.token}"})
            response.raise_for_status()  # Lanzar una excepción para respuestas incorrectas (4xx o 5xx)

            # Parsear la respuesta JSON
            repo_data = response.json()

            # Extraer la información adicional del repositorio
            name = repo_data.get("name", "")
            owner = repo_data.get("owner", {}).get("login", "")
            forks = repo_data.get("forks_count", 0)
            stars = repo_data.get("stargazers_count", 0)
            default_branch = repo_data.get("default_branch", "")
            open_issues = repo_data.get("open_issues_count", 0)
            creation_date = repo_data.get("created_at", "")
            github_link = repo_data.get("html_url", "")

            # Crear una nueva instancia de repositorio con la información adicional
            new_repo = repository(
                name=name,
                owner=owner,
                forks=forks,
                stars=stars,
                default_branch=default_branch,
                open_issues=open_issues,
                creation_date=datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%SZ"),
                github_link=github_link,
                user_id=user_id
            )

            # Obtener al usuario y agregar el nuevo repositorio a la lista
            user = session.query(Users).filter_by(id=user_id).first()
            user.repositorys.append(new_repo)

            # Agregar el nuevo repositorio a la sesión y confirmar los cambios
            session.add(new_repo)
            session.commit()

            return 1

    except requests.exceptions.RequestException as e:
        return 2
    except IntegrityError as e:
        return 3



def get_user_id(name):
    """
    Get the user id from the database with the given name.
    """
    with Session(engine) as session:
        user = session.query(Users).filter_by(name=name).first()
        return user.id
    
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

def get_details_repositorie(id):
    session = Session(engine)
    repo = session.query(repository).filter_by(id=id).first()
    session.close()
    return repo