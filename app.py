import os
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory
from werkzeug.utils import secure_filename

from db_actions import exec_return, exec_noreturn
from categories import CATEGORIES

APP_FOLDER = os.path.realpath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(APP_FOLDER, "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    # ha be lennenk jelentkezve, menjunk is tovabb a profilra
    if 'nick' in session:
        return redirect(url_for('profile'))
    # regisztracio lenyilo listahoz telepulesek listaja
    settlements = exec_return("SELECT Id, Name FROM Settlements ORDER BY Name")[1]
    errormsg = ""  # inicializaljuk. Ennek erteket fogjuk alertben megjeleniteni, ha hiba adodik
    # formok kezelese
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
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    # nick lekerese
    nick = session.get('nick')
    # szemelyes adatok modositasanal lenyilo listahoz telepulesek listaja
    settlements = exec_return("SELECT Id, Name FROM Settlements ORDER BY Name")[1]
    own_pictures = exec_return(f"SELECT Filename, Description FROM Pictures WHERE author = '{nick}'")[1]
    errormsg = ""  # inicializaljuk. Ennek erteket fogjuk alertben megjeleniteni, ha hiba adodik
    # formok kezelese
    if request.method == 'POST':
        form_data = request.form  # bekerjuk a formok adatait
        if 'personalhidden' in form_data:  # a hidden input tagek neve szerint dontunk, melyik form volt
            # adatok valtozokba
            fullname = form_data.get('fullname')
            email = form_data.get('email')
            password = form_data.get('password')
            passwordagain = form_data.get('passwordagain')
            location = form_data.get('location')
            birthdate = form_data.get('birthdate')
            # olyan validacio, amire a html nem volt eleg (jelszo es nick egyedisege)
            correct = True
            if len(password.strip()) != 0:
                if len(password) < 8:
                    errormsg += "A jelszónak legalább 8 karakter hosszúnak kell lennie. "
                    correct = False
                if password != passwordagain:
                    errormsg += "A két jelszó nem egyezik. "
                    correct = False
            else:
                passwordquery = exec_return(f"SELECT password FROM Users WHERE nick = '{nick}'")
                password = passwordquery[1][0][0]
            # ha a selecten nem valasztott a juzer mas lokaciot, akkor annak feliratabol kell decryptelni
            if ':' in location:
                locationname = location.split(":")[1].strip()
                locationquery = exec_return(f"SELECT Id FROM Settlements WHERE name = '{locationname}'")
                location = locationquery[1][0][0]
            # mentsuk el a modositott adatokat
            if correct:
                exec_noreturn(f"""UPDATE Users\
                                    SET email = '{email}', password = '{password}', fullname = '{fullname}',\
                                    location = {location}, birthdate = TO_DATE('{birthdate}', 'YYYY-MM-DD')\
                                    WHERE nick = '{nick}'""")

        # fájlfeltöltés
        elif 'uploadpic' in request.files:
            upload(form_data, nick)

    # szemelyes adatok lekerese
    personaldata = exec_return(f"""SELECT nick, email, password, fullname, Settlements.name, Countries.name, birthdate\
                                    FROM Users, Settlements, Countries\
                                    WHERE nick = '{nick}'\
                                    and Users.location = Settlements.Id and Settlements.country = Countries.Id""")

    return render_template('profile.html', personaldata=personaldata, settlements=settlements, categories=CATEGORIES,
                           own_pictures=own_pictures, errormsg=errormsg)


@app.route('/uploadpic', methods=['POST'])
def upload(form_data, nick):
    errormsg = ""  # inicializaljuk. Ennek erteket fogjuk alertben megjeleniteni, ha hiba adodik
    file = request.files['uploadpic']
    extension = file.filename.rsplit('.', 1)[1]
    correct = True
    if file.filename == '':
        errormsg += "Nincs kiválasztott kép. "
        correct = False
    if file and '.' in file.filename and extension.lower() in ALLOWED_EXTENSIONS:
        # adatok lementese valtozokba
        filename = secure_filename(str(datetime.now()) + "." + extension)
        title = form_data.get('title')
        location = form_data.get('location')
        category = form_data.get('category')
        description = form_data.get('description')
        if len(description) > 150:
            errormsg += "A leiras maximum 150 karakter hosszú lehet. "
            correct = False
        # ha a selecten nem valasztott a juzer mas lokaciot, akkor annak feliratabol kell decryptelni
        if ':' in location:
            locationname = location.split(":")[1].strip()
            locationquery = exec_return(f"SELECT Id FROM Settlements WHERE name = '{locationname}'")
            location = locationquery[1][0][0]
        # uploads folderbe mentése a kepnek
        if correct:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # kep feltoltese az adatbazisba, kategoria megadasa
            exec_noreturn(
                f"INSERT INTO Pictures VALUES ('{filename}', '{nick}', '{title}', '{description}', '{location}' )")
            exec_noreturn(f"INSERT INTO Categories VALUES ('{category}', '{filename}')")
    else:
        errormsg += "Az érvényes fájltípusok: png, jpg, jpeg, gif. "


# feltoltott kép jelenjen meg a pictures.html-ben
@app.route('/uploadpic/<filename>')
def send_image(filename):
    return send_from_directory("uploads", filename)


# képeink oldal tartalma
@app.route('/pictures')
def get_images():
    author = session.get('nick')
    image_names = dict()
    i = 0
    # az uploads-ban lévő képek kilistázása
    images_dir = os.listdir(app.config['UPLOAD_FOLDER'])
    # az adatbázisban lévő képek kilistázása
    images_database = exec_return(f"SELECT Filename, Description FROM Pictures")
    for image in images_dir:
        # mivel tuple-t ad vissza az adatbazis ezert a másodikban lévő lista fájlneveit át kell alakítani str-é
        if image in (str(images_database[1])):
            # megegyező nevű képeket dictionarybe gyűjtük a {kép neve : leiras }
            image_names.update({image: images_database[1][i][1]})
            i += 1
    return render_template("pictures.html", image_names=image_names)


# categories.html
@app.route('/categories')
def categories():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    # parameterben kapott kategoria
    chosencategory = request.args.get('cat')
    # fajlnevek lekerese a kapott kategoriabol
    photos_from_category = []
    chosen_category_count = 0
    if chosencategory is not None:
        photos_from_category = exec_return(f"SELECT Pictureid FROM Categories where name = '{chosencategory}'")[1]
        chosen_category_count = exec_return(f"SELECT COUNT(*) FROM Categories where name = '{chosencategory}'")[1][0][0]
    return render_template('categories.html', categories=CATEGORIES, chosencategory=chosencategory,
                           chosencategorycount=chosen_category_count, photos=photos_from_category)


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


# fenykepeink oldal
@app.route('/pictures')
def pictures():
    if 'nick' not in session:
        return redirect(url_for('index'))
    return render_template('pictures.html')


if __name__ == "__main__":
    app.run(debug=True)
