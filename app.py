from flask import Flask, render_template, request, url_for, redirect, session
from db_actions import exec_return, exec_noreturn

app = Flask(__name__)
app.secret_key = "super secret key"


# index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    # ha be lennenk jelentkezve, menjunk is tovabb a profilra
    if 'nick' in session:
        return redirect(url_for('profile'))
    # regisztracio lenyilo listahoz telepulesek listaja
    settlements = exec_return("SELECT Id, Name FROM Settlements ORDER BY Name")[1]
    errormsg = ""  # inicializaljuk. Ennek erteket fogjuk alertben megjeleniteni, ha hiba adodik
    if request.method == 'POST':
        form_data = request.form  # bekerjuk a form adatait
        if 'login' in form_data:  # a hidden input tagek neve szerint dontunk, login vagy signup-e
            # juzer bejelentkeztetese
            login_email = form_data.get('loginemail')
            login_password = form_data.get('loginpassword')
            check_user = exec_return(f"SELECT email, password, nick FROM Users WHERE email = '{login_email}'")
            if check_user[1]:  # True, ha letezik a felhasznalo
                if check_user[1][0][1] == login_password:  # mert egy kételemű lista egyetlen elemének második eleme...
                    session['nick'] = check_user[1][0][2]
                    session.permanent = True
                    return redirect(url_for('profile'))
                else:
                    errormsg = "A megadott jelszó hibás."
            else:
                errormsg = "A megadott e-mail helytelen."
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
            check_nick = exec_return(f"SELECT nick FROM Users WHERE nick = '{nick}'")
            if check_nick[1]:  # True, ha nem ures
                errormsg += "A beírt nicknév már foglalt. "
                correct = False
            if len(location) < 1:
                errormsg += "Adja meg a települést, ahonnan származik. "
                correct = False
            # juzer elmentese
            if correct:
                exec_noreturn(
                    f"INSERT INTO Users VALUES('{nick}', '{email}', '{password}', '{fullname}', {location}, TO_DATE('{birthdate}', 'YYYY-MM-DD'))")
                session['nick'] = nick
                session.permanent = True
                return redirect(url_for('profile'))
    return render_template('index.html', settlements=settlements, errormsg=errormsg)


# profile.html
@app.route('/profile')
def profile():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    data = exec_return("SELECT * FROM Countries")
    return render_template('profile.html', colnames=data[0], rows=data[1])


# categpries.html
@app.route('/categories')
def categories():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    return render_template('categories.html')


# mostactive.html
@app.route('/mostactive')
def mostactive():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    return render_template('mostactive.html')


# worldmap.html
@app.route('/worldmap')
def worldmap():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    return render_template('worldmap.html')


# logout process
@app.route('/logout')
def logout():
    session.pop('nick', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
