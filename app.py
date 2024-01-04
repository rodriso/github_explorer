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
    return render_template('main.html')

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
