from flask import Flask, render_template, request, url_for, redirect
from db_actions import execute

app = Flask(__name__)


# index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    # regisztracio lenyilo listahoz telepulesek listaja
    settlements = execute("SELECT Id, Name FROM Settlements ORDER BY Name")[1]
    errormsg = ""  # inicializaljuk. Ennek erteket fogjuk alertben megjeleniteni, ha hiba adodik
    if request.method == 'POST':
        form_data = request.form  # bekerjuk a form adatait
        if 'login' in form_data:  # a hidden input tagek neve szerint dontunk, login vagy signup-e
            # juzer bejelentkeztetese
            login_email = form_data.get('loginemail')
            login_password = form_data.get('loginpassword')
            # TODO: check if benne van-e a juzer az adatbazisban
            return redirect(url_for('profile'))
        elif 'signup' in form_data:
            # adatok valtozokba
            email = form_data.get('email')
            password = form_data.get('password')
            passwordagain = form_data.get('passwordagain')
            nick = form_data.get('nick')
            fullname = form_data.get('fullname')
            location = form_data.get('location')
            birthdate = form_data.get('birthdate')
            # olyan validacio, amire a html nem volt eleg (jelszo es nick egyedisege)
            correct = True
            if len(password) < 8:
                errormsg += "A jelszónak legalább 8 karakter hosszúnak kell lennie. "
                correct = False
            if password != passwordagain:
                errormsg += "A két jelszó nem egyezik. "
                correct = False
            check_nick = execute(f"SELECT nick FROM Users WHERE nick = '{nick}'")
            if check_nick[1]:   # True, ha nem ures
                errormsg += "A beírt nicknév már foglalt. "
                correct = False
            if len(location) < 1:
                errormsg += "Adja meg a települést, ahonnan származik. "
                correct = False
            # TODO: convert date (error: expected DATE got NUMBER)
            # juzer elmentese
            if correct:
                execute(f"INSERT INTO Users VALUES('{nick}', '{email}', '{password}', '{fullname}', {location}, {birthdate})")
                return redirect(url_for('profile'))
    return render_template('index.html', settlements=settlements, errormsg=errormsg)


# profile.html
@app.route('/profile')
def profile():
    data = execute("SELECT * FROM Countries")
    return render_template('profile.html', colnames=data[0], rows=data[1])


# categpries.html
@app.route('/categories')
def categories():
    return render_template('categories.html')


# mostactive.html
@app.route('/mostactive')
def mostactive():
    return render_template('mostactive.html')


# worldmap.html
@app.route('/worldmap')
def worldmap():
    return render_template('worldmap.html')


if __name__ == "__main__":
    app.run(debug=True)
