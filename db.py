"""

Modulo SQLAlchemy
Este modulo define la estructura de la base de datos y las funciones para interactuar con ella.

"""

import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey,desc,DateTime,create_engine
from sqlalchemy.orm import DeclarativeBase,Session,relationship
import requests
from dotenv import load_dotenv

load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")
databasename = os.getenv("DATABASE_NAME")
class Base(DeclarativeBase):
    """Base class for all database models."""

class Users(Base):
    """User account model."""
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)
    repositorys = relationship(
        "Repository", back_populates="user", cascade="all, delete-orphan"
    )

#Tabla de repositorios
class Repository(Base):
    """Repository model."""
    __tablename__ = "repositorys"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(String)
    forks = Column(Integer)
    stars = Column(Integer)
    default_branch = Column(String)
    open_issues = Column(Integer)
    creation_date = Column(DateTime)
    github_link = Column(String)
    user_id = Column(Integer, ForeignKey("user_account.id"))
    user = relationship("Users", back_populates="repositorys")
    last_update = Column(DateTime)
    times_added = Column(Integer, default=0)

#Creación de la base de datos
engine = create_engine(f"sqlite:///./{databasename}.db", echo=True)
Base.metadata.create_all(engine)




def get_repo(user_id: int):
    """
    Retrieves the repository associated with a given user ID.
    
    Parameters:
        user_id (int): The ID of the user.
    
    Returns:
        list: A list of repository objects associated with the user. 
        If the user ID is not found, an empty list is returned.
    """
    with Session(engine) as session:
        user = session.query(Users).get(user_id)
        if user:
            return user.repositorys
        return []


def add_repository(repo_name: str, user_id: int) -> bool:
    """
    Add a repository to the database or its updated if it exists on the database 
    and its added to the user.
    Args:
        repo_name (str): The name of the repository in the format "owner/repo".
        user_id (int): The ID of the user who is adding the repository.

    Returns:
        bool: True if the repository was successfully added, False otherwise.
    """
    api_url = f"https://api.github.com/repos/{repo_name}"

    try:
        with Session(engine) as session:
            # Hacer una solicitud GET a la API de GitHub con el encabezado de Autorización
            try:
                response = requests.get(api_url,
                                        headers={"Authorization": f"token {github_token}"},
                                        timeout=10)
                response.raise_for_status()  # Lanzar una excepción para respuestas incorrectas
                # Parsear la respuesta JSON
                repo_data = response.json()
            except requests.exceptions.RequestException:
                return False
            # Parsear la respuesta JSON
            user = get_user_with_id(user_id, session)
            # Extraer la información adicional del repositorio
            name, owner, forks, stars, \
            default_branch, open_issues, creation_date, github_link = extract_data(repo_data)

            new_repo = session.query(Repository).filter_by(name=name, owner=owner).first()
            if new_repo is not None:
                update_repository(int(new_repo.id))
                #Comprobar si el usuario no tiene este repositorio ya.
                if new_repo not in user.repositorys:
                    new_repo.times_added += 1
                    user.repositorys.append(new_repo)
                session.commit()
                return True
            # Crear una nueva instancia de repositorio con la información adicional.
            new_repo = create_new_repo(
            user_id, name, owner, forks, stars,
            default_branch, open_issues, creation_date, github_link
            )# Obtener al usuario y agregar el nuevo repositorio a la lista.
            user.repositorys.append(new_repo)
            session.add(new_repo)
            session.commit()
            return True
    except requests.exceptions.RequestException:
        return False

def get_user_with_id(user_id,session):
    """
    Retrieves a user with the specified user ID from the session.

    Args:
        user_id (int): The ID of the user to retrieve.
        session (Session): The session object used for querying the database.

    Returns:
        User: The user object with the specified user ID, or None if no user is found.
    """
    return session.query(Users).filter_by(id=user_id).first()
def create_new_repo(user_id, name, owner,
                    forks, stars, default_branch,
                    open_issues, creation_date, github_link):
    """
    Creates a new repository with the given parameters.

    Parameters:
        user_id (int): The ID of the user who owns the repository.
        name (str): The name of the repository.
        owner (str): The owner of the repository.
        forks (int): The number of forks the repository has.
        stars (int): The number of stars the repository has.
        default_branch (str): The default branch of the repository.
        open_issues (int): The number of open issues in the repository.
        creation_date (str): The creation date of the repository in the format "%Y-%m-%dT%H:%M:%SZ".
        github_link (str): The link to the repository on GitHub.
        times_added (int): The number of times the repository has been added.

    Returns:
        Repository: The newly created repository object.
    """
    return Repository(
                name=name,
                owner=owner,
                forks=forks,
                stars=stars,
                default_branch=default_branch,
                open_issues=open_issues,
                creation_date= datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%SZ"),
                github_link=github_link,
                user_id=user_id,
                last_update=datetime.now(),
                times_added =+ 1
            )

def extract_data(repo_data):
    """
    Extracts data from a repository object.
    
    Args:
        repo_data (dict): A dictionary containing information about a repository.
        
    Returns:
        tuple: A tuple containing the extracted data from the repository. 
        The tuple contains the following elements:
            - name (str): The name of the repository.
            - owner (str): The owner of the repository.
            - forks (int): The number of forks the repository has.
            - stars (int): The number of stars the repository has.
            - default_branch (str): The default branch of the repository.
            - open_issues (int): The number of open issues the repository has.
            - creation_date (str): The creation date of the repository.
            - github_link (str): The GitHub link of the repository.
    """
    name = repo_data.get("name", "")
    owner = repo_data.get("owner", {}).get("login", "")
    forks = repo_data.get("forks_count", 0)
    stars = repo_data.get("stargazers_count", 0)
    default_branch = repo_data.get("default_branch", "")
    open_issues = repo_data.get("open_issues_count", 0)
    creation_date = repo_data.get("created_at", "")
    github_link = repo_data.get("html_url", "")
    return name,owner,forks,stars,default_branch,open_issues,creation_date,github_link

def update_repository(repo_id: int) -> bool:
    """
    Update the repository information in the database.

    Args:
        repo_id (int): The ID of the repository to be updated.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    with Session(engine) as session:
        # Retrieve the repository from the database
        repo = session.query(Repository).filter_by(id=repo_id).first()
        if repo:
            try:
                # Pedir la información de GitHub desde su API
                try:
                    api_url = f"https://api.github.com/repos/{repo.owner}/{repo.name}"
                    response = requests.get(api_url,
                                            headers={"Authorization": f"token {github_token}"},
                                            timeout= 10)
                    response.raise_for_status()
                    repo_data = response.json()
                except requests.exceptions.RequestException:
                    return False
                (name, owner, forks, stars,
                default_branch, open_issues, creation_date, github_link) = extract_data(repo_data)


                # Actualizar la información del repositorio
                repo.name = name
                repo.owner = owner
                repo.forks = forks
                repo.stars = stars
                repo.default_branch = default_branch
                repo.open_issues = open_issues
                repo.creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%SZ")
                repo.github_link = github_link

                # Update the last_update timestamp
                repo.last_update = datetime.now()

                # Commit the changes to the database
                session.commit()

                return True
            except requests.exceptions.RequestException:
                return False
        else:
            return False



def get_user_id(name):
    """
    Get the user ID based on the provided name.

    Parameters:
        name (str): The name of the user.

    Returns:
        int: The ID of the user.
    """
    with Session(engine) as session:
        user = session.query(Users).filter_by(name=name).first()
        return user.id
def add_user(name, password):
    """
    Adds a new user to the database with the given name and password.
    
    Args:
        name (str): The name of the user.
        password (str): The password for the user.
    
    Returns:
        bool: True if the user was successfully added, False otherwise.
    """
    with Session(engine) as session:
        user = Users(name=name, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user is not None
def check_user(name):
    """
    Check if the user exists.

    Args:
        name (str): The name of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    #Check the user
    session = Session(engine)
    user = session.query(Users).filter_by(name=name).first()
    session.close()

    return user is not None

def check_user_and_password(name, password):
    """
    Check the user and password.

    Args:
        name (str): The name of the user.
        password (str): The password of the user.

    Returns:
        bool: True if the user and password match, False otherwise.
    """

    session = Session(engine)
    user = session.query(Users).filter_by(name=name, password=password).first()
    session.close()

    return user is not None

def get_details_repositorie(repoid):
    """
    Retrieve details of a repository based on its ID.

    Parameters:
        id (int): The ID of the repository to retrieve details for.

    Returns:
        repository: The repository object containing the details.
    """

    session = Session(engine)
    repo = session.query(Repository).filter_by(id=repoid).first()
    session.close()
    return repo


def get_top_repositories():
    """
    Retrieves the top 3 repositories based on the 'times_added' count.
    
    Returns:
        list: A list of tuples containing the repository name and the 'times_added' count.
    """
    with Session(engine) as session:
        query = (
            #Añadir mas elementos si se desea ampliar la información del top 3 de la pagina.
            session.query(Repository,Repository.name,Repository.times_added,Repository.github_link)
            .order_by(desc(Repository.times_added))
            .limit(3)
        )

        result = query.all()

        return result
