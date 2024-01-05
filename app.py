from flask import Flask
from markupsafe import escape
from flask import url_for,render_template,request,redirect,session,flash
import db

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate(username, password):
            flash('You were successfully logged in')
            session['logged_in_user'] = username
            return redirect(url_for('main'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error, username=username)



@app.route('/main/', methods=['POST', 'GET'])

def main():
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))
    
    get_repos = db.get_repo(db.get_user_id(session['logged_in_user']))
    return render_template('main.html', repos=get_repos)

@app.route('/add_repo/', methods=['POST', 'GET'])
def add_repo():
    error = None

    # Check if the user is logged in
    if 'logged_in_user' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    # Check if the request method is POST
    elif request.method == 'POST':
        repo_name = request.form['repo_name']
        user_id = db.get_user_id(session['logged_in_user'])

        # Assuming db.add_repository returns True if added successfully
        repository = db.add_repository(repo_name, user_id)
        if repository == 1:
            flash('Repository añadido')
            # Get the updated list of repositories
            repos = db.get_repo(user_id)
            # Pass the updated list to the template
            return render_template('main.html', repos=repos)

        elif repository == 2:
            error = 'Has introducido mal el nombre del repositorio (Recuerda el formato nombre/repositorio)'
        elif repository == 3:
            error = 'Error desconocido'
        

    # If not a POST request or if adding repository fails, render the add_repo.html template
    return render_template('add_repo.html', error=error)

@app.route("/details/<repo_id>")
def details(repo_id):
    repo = db.get_details_repositorie(repo_id)
    return render_template('details.html', repo = repo)


@app.route("/register/", methods=['POST', 'GET'])

def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not db.check_user(username):
            if db.add_user(username, password):
                session['logged_in_user'] = username
                flash('You were successfully registered')
                return redirect(url_for('main'))
        else:
            error = 'Este usuario ya está elegido. Por favor, elija otro.'
    return render_template('register.html', error=error)


@app.route("/logout")
def logout():
    session.pop('logged_in_user', None)
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def authenticate(username, password):
    #@TODO Autenticarse en la base de datos
    return db.check_user_and_password(username, password)
