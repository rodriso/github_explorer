from flask import Flask
from flask import url_for,render_template,request,redirect,session,flash
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
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not db.check_user(username):
            if db.add_user(username, password):
                session['logged_in_user'] = username
                flash('¡Te has registrado correctamente!')
                return redirect(url_for('main'))
        else:
            error = 'Este usuario ya está elegido. Por favor, elija otro.'
    return render_template('register.html', error=error)


###################################################################################
#RF2: Login / Logout del usuario
###################################################################################
@app.route("/logout")
def logout():
    session.pop('logged_in_user', None)
    return redirect(url_for('login'))

@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate(username, password):
            flash('¡Has inciado sesión correctamente!')
            session['logged_in_user'] = username
            return redirect(url_for('main'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error, username=username)



###################################################################################
#RF3: Listar repositorios de GitHub
###################################################################################
@app.route('/main/', methods=['POST', 'GET'])

def main():
    if check_logged():
        return to_login()
    user_id = db.get_user_id(session['logged_in_user'])
    get_repos = db.get_repo(user_id)
    ###################################################################################
    #RF8: Trending repositorios en GitHub Explorer
    ###################################################################################
    top_repositories = db.get_top_repositories()
    return render_template('main.html', repos=get_repos,user_id=user_id,top_repositories=top_repositories)

###################################################################################
#RF4: Añadir repositorio de GitHub
###################################################################################


@app.route('/add_repo/', methods=['POST', 'GET'])
def add_repo():
    error = None

    if check_logged():
        return to_login()
    
    elif request.method == 'POST':
        user_id, repository = add_new_repository()
        if repository:
            flash('Repositorio añadido')
            # Conseguir la lista actualizada de repositorios
            repos = db.get_repo(user_id)
            top_repositories = db.get_top_repositories()
            user_id = db.get_user_id(session['logged_in_user'])
            return render_template('main.html', repos=repos,user_id=user_id,top_repositories=top_repositories)
        else:
            error = throw_error_repository()
        

    # If not a POST request or if adding repository fails, render the add_repo.html template
    return render_template('add_repo.html', error=error)

###################################################################################
#RF5: Mostrar detalles de un repositorio de GitHub
###################################################################################

@app.route("/details/<repo_id>") 
def details(repo_id):
    repo = db.get_details_repositorie(repo_id)
    user_id = db.get_user_id(session['logged_in_user'])
    return render_template('details.html', repo = repo , user_id = user_id)

###################################################################################
#RF6: Actualizar repositorio de GitHub
###################################################################################
@app.route('/update_repository/<repo_id>', methods=['POST'])
def update_repository(repo_id):
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
    #@TODO Autenticarse en la base de datos
    return db.check_user_and_password(username, password)
def throw_error_repository():
    return 'Has introducido mal el nombre del repositorio (Recuerda el formato nombre/repositorio)'

def add_new_repository():
    repo_name, user_id = get_data_repositorie()
    repository = db.add_repository(repo_name, user_id)
    return user_id,repository

def get_data_repositorie():
    repo_name = request.form['repo_name']
    user_id = db.get_user_id(session['logged_in_user'])
    return repo_name,user_id

def to_login():
    return redirect(url_for('login'))

def check_logged():
    return 'logged_in_user' not in session

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


