"""
Flask App Module

Este módulo contiene la aplicación Flask principal.
"""
import sys
from flask import Flask
from flask import url_for,render_template,request,redirect,session,flash
sys.path.append('.')
import db

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
@app.route("/")
def index():

    """
    Redirects the user to the login page.

    Returns:
        None
    """
    return redirect(url_for('login'))
###################################################################################
#RF1: Registrar un usuario
###################################################################################
@app.route("/register/", methods=['POST', 'GET'])
def register():
    """
    Handle registration for the user.

    This function handles the registration process for a user by receiving a
    POST request with the user's username and password. It then calls the
    `handle_registration` function to handle the registration logic.

    Parameters:
    - None

    Returns:
    - None

    """
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        registration_result = handle_registration(username, password)

        if registration_result["success"]:
            flash('¡Te has registrado correctamente!')
            return redirect(url_for('main'))
        error = registration_result["error"]

    return render_template('register.html', error=error)
###################################################################################
#RF2: Login / Logout del usuario
###################################################################################
@app.route("/logout")
def logout():
    """
    Logs out the current user by removing the 'logged_in_user' key from the session.
    
    """
    session.pop('logged_in_user', None)
    return redirect(url_for('login'))

@app.route('/login/', methods=['POST', 'GET'])
def login():
    """
    Logs in a user by authenticating their username and password.

    """
    error = None
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            flash('¡Has inciado sesión correctamente!')
            session['logged_in_user'] = username
            return redirect(url_for('main'))
        error = 'Usuario o contraseña incorrecta.'
    return render_template('login.html', error=error, username=username)



###################################################################################
#RF3: Listar repositorios de GitHub
###################################################################################
@app.route('/main/', methods=['POST', 'GET'])
def main():
    """
    Retrieves the main page of the application.

    Returns:
        str: The rendered HTML template of the main page.

    """
    if check_logged():
        return to_login()

    user_id = db.get_user_id(session['logged_in_user'])
    repos, top_repositories = fetch_repository_data(user_id)

    return render_template('main.html',
                           repos=repos, user_id=user_id,
                           top_repositories=top_repositories)
###################################################################################
#RF4: Añadir repositorio de GitHub
###################################################################################
@app.route('/add_repo/', methods=['POST', 'GET'])
def add_repo():
    """
    Function to handle the '/add_repo/' route. 

    Parameters:
        None.

    Returns:
        The rendered template for adding a repository, or a redirect to the login page if the user is not logged in, or an error message if there was an issue adding the repository.
    """
    error = None
    if check_logged():
        return to_login()

    if request.method == 'POST':
        user_id, repository = add_new_repository()

        if repository:
            flash('Repositorio añadido')
            return redirect_after_repo_added(user_id)

        error = throw_error_repository()

    return render_add_repo_template(error)
###################################################################################
#RF5: Mostrar detalles de un repositorio de GitHub
###################################################################################
@app.route("/details/<repo_id>")
def details(repo_id):
    """
    Retrieves the details of a repository based on its ID and renders the 'details.html' template.

    Parameters:
        repo_id (str): The ID of the repository to retrieve details for.

    Returns:
        str: The rendered 'details.html' template with the repository details and the user ID.
    """
    if check_logged():
        return to_login()
    repo, user_id = fetch_repository_details(repo_id)

    return render_template('details.html', repo=repo, user_id=user_id)

###################################################################################
#RF6: Actualizar repositorio de GitHub
###################################################################################
@app.route('/update_repository/<repo_id>', methods=['POST'])
def update_repository(repo_id):
    """
    Update a repository in the database based on the given repo_id.

    Parameters:
        repo_id (int): The ID of the repository to be updated.

    Returns:
        None
    """
    success = db.update_repository(int(repo_id))

    if success:
        flash('Repositorio actualizado')
    else:
        flash('¡Error al actualizar el repositorio!')

    return redirect(url_for('details', repo_id=repo_id))



###################################################################################
#Funciones para la funcionalidad de la parte de flask
###################################################################################
def authenticate(username, password):
    """
    Authenticate a user with a username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """
    #@TODO Autenticarse en la base de datos
    return db.check_user_and_password(username, password)
def throw_error_repository():
    """
    Throws an error indicating that the repository name was entered incorrectly.
    
    Returns:
        str: The error message indicating the incorrect repository name format.
    """
    return 'Has introducido mal el nombre del repositorio (Recuerda el formato nombre/repositorio)'
def add_new_repository():
    """
    Add a new repository to the database.

    Args:
        None

    Returns:
        Tuple: The user ID and the newly created repository.
    """
    repo_name, user_id = get_data_repositorie()
    repository = db.add_repository(repo_name, user_id)
    return user_id,repository
def get_data_repositorie():
    """
    Retrieves the repository name and user ID from the request form and the database.

    Returns:
        A tuple containing the repository name (str) and the user ID (int).
    """
    repo_name = request.form['repo_name']
    user_id = db.get_user_id(session['logged_in_user'])
    return repo_name,user_id
def to_login():
    """
    Redirects the user to the login page.

    Returns:
        None
    """
    return redirect(url_for('login'))
def check_logged():
    """
    Check if the user is logged in.

    Returns:
        bool: True if the user is not logged in, False otherwise.
    """
    return 'logged_in_user' not in session
@app.errorhandler(404)
def page_not_found(error):
    """
    A function that handles the 404 error.

    :return: A tuple containing the rendered template and the HTTP status code.
    """
    return render_template('404.html',error = error), 404
def fetch_repository_details(repo_id):
    """
    Fetches repository details and user ID for rendering.

    Parameters:
        repo_id (str): The ID of the repository.

    Returns:
        Tuple: A tuple containing the repository details and the user ID.
    """
    repo = db.get_details_repositorie(repo_id)
    user_id = db.get_user_id(session['logged_in_user'])

    return repo, user_id
def redirect_after_repo_added(user_id):
    """
    Retrieves the repositories associated with the given user ID from the database.

    Args:
        user_id (int): The ID of the user whose repositories should be retrieved.

    Returns:
        list: A list of repository objects associated with the user.

    Raises:
        DatabaseError: If there is an error retrieving the repositories from the database.
    """
    repos = db.get_repo(user_id)
    top_repositories = db.get_top_repositories()
    user_id = db.get_user_id(session['logged_in_user'])
    return render_template('main.html', repos=repos,
                           user_id=user_id, top_repositories=top_repositories)
def render_add_repo_template(error):
    """
    Renders the 'add_repo.html' template with the provided error message.

    Parameters:
        error (str): The error message to be displayed on the template.

    Returns:
        str: The rendered HTML content of the 'add_repo.html' template.
    """
    return render_template('add_repo.html', error=error)
def fetch_repository_data(user_id):
    """
    Fetches repository data for the logged-in user.

    Parameters:
        user_id (int): The ID of the logged-in user.

    Returns:
        Tuple: A tuple containing a list of user repositories and a list of top repositories.
    """
    user_repos = db.get_repo(user_id)
    top_repositories = db.get_top_repositories()
    return user_repos, top_repositories
def handle_registration(username, password):
    """
    Handle the registration process for a user.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        dict: A dictionary containing the registration result.
            - success (bool): Indicates if the registration was successful or not.
            - error (str): An error message if the registration failed.

    Raises:
        None
    """
    registration_result = {"success": False, "error": None}

    if not db.check_user(username):
        if db.add_user(username, password):
            session['logged_in_user'] = username
            registration_result["success"] = True
        else:
            registration_result["error"] = 'Error al registrar al usuario.'
    else:
        registration_result["error"] = 'Este usuario ya está elegido. Por favor, elija otro.'

    return registration_result
