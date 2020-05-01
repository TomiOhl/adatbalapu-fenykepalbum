import os
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory, flash
from werkzeug.utils import secure_filename

from db_actions import exec_return, exec_noreturn
from categories import CATEGORIES
from settlements import get_settlements

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
    settlements = get_settlements()
    # formok kezelese
    if request.method == 'POST':
        form_data = request.form  # bekerjuk a form adatait
        if 'login' in form_data:  # a hidden input tagek neve szerint dontunk, login vagy signup-e
            # juzer bejelentkeztetese
            login_email = form_data.get('loginemail')
            login_password = form_data.get('loginpassword')
            check_user = exec_return(
                "SELECT email, password, nick FROM Users WHERE email = :login_email", [login_email])
            if check_user[1]:  # True, ha letezik a felhasznalo
                if check_user[1][0][1] == login_password:  # mert egy kételemű lista egyetlen elemének második eleme...
                    session['nick'] = check_user[1][0][2]
                    session.permanent = True
                    return redirect(url_for('profile'))
                else:
                    flash("A megadott jelszó hibás.")
            else:
                flash("A megadott e-mail helytelen.")
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
                flash("A jelszónak legalább 8 karakter hosszúnak kell lennie. ")
                correct = False
            if password != passwordagain:
                flash("A két jelszó nem egyezik. ")
                correct = False
            check_nick = exec_return("SELECT nick FROM Users WHERE nick = :nick", [nick])
            if check_nick[1]:  # True, ha nem ures
                flash("A beírt nicknév már foglalt. ")
                correct = False
            if len(location) < 1:
                flash("Adja meg a települést, ahonnan származik. ")
                correct = False
            # juzer elmentese
            if correct:
                exec_noreturn("""INSERT INTO Users\
                            VALUES(:nick, :email, :password, :fullname, :location, TO_DATE(:birthdate, 'YYYY-MM-DD'))\
                                """, [nick, email, password, fullname, location, birthdate])
                session['nick'] = nick
                session.permanent = True
                return redirect(url_for('profile'))
    return render_template('index.html', settlements=settlements)


# profile.html
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    # nick lekerese
    nick = session.get('nick')
    # szemelyes adatok modositasanal lenyilo listahoz telepulesek listaja
    settlements = get_settlements()
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
                    flash("A jelszónak legalább 8 karakter hosszúnak kell lennie. ")
                    correct = False
                if password != passwordagain:
                    flash("A két jelszó nem egyezik. ")
                    correct = False
            else:
                passwordquery = exec_return("SELECT password FROM Users WHERE nick = :nick", [nick])
                password = passwordquery[1][0][0]
            # ha a selecten nem valasztott a juzer mas lokaciot, akkor annak feliratabol kell decryptelni
            if ':' in location:
                locationname = location.split(":")[1].strip()
                locationquery = exec_return("SELECT Id FROM Settlements WHERE name = :locationname", [locationname])
                location = locationquery[1][0][0]
            # mentsuk el a modositott adatokat
            if correct:
                exec_noreturn("""UPDATE Users\
                                    SET email = :email, password = :password, fullname = :fullname,\
                                    location = :location, birthdate = TO_DATE(:birthdate, 'YYYY-MM-DD')\
                                    WHERE nick = :nick""", [email, password, fullname, location, birthdate, nick])

        # fájlfeltöltés
        elif 'uploadpic' in request.files:
            upload(form_data, nick)

    # szemelyes adatok lekerese
    personaldata = exec_return("""SELECT nick, email, password, fullname, Settlements.name, Countries.name, birthdate\
                                    FROM Users, Settlements, Countries\
                                    WHERE nick = :nick\
                                    and Users.location = Settlements.Id and Settlements.country = Countries.Id""",
                               [nick])
    # sajat kepek megjelenitese
    own_pictures = exec_return("""SELECT Filename, Title, Description, Location, Categories.Name\
                                    FROM Pictures, Categories WHERE Author = :nick AND Filename = Pictureid""",
                               [nick])[1]

    return render_template('profile.html', personaldata=personaldata, settlements=settlements, categories=CATEGORIES,
                           own_pictures=own_pictures)


@app.route('/uploadpic', methods=['POST'])
def upload(form_data, nick):
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    file = request.files['uploadpic']
    extension = file.filename.rsplit('.', 1)[1]
    correct = True
    if file.filename == '':
        flash("Nincs kiválasztott kép. ")
        correct = False
    if file and '.' in file.filename and extension.lower() in ALLOWED_EXTENSIONS:
        # adatok lementese valtozokba
        filename = secure_filename(str(datetime.now()) + "." + extension)
        title = form_data.get('title')
        location = form_data.get('location')
        category = form_data.get('category')
        description = form_data.get('description')
        if len(description) > 150:
            flash("A leiras maximum 150 karakter hosszú lehet. ")
            correct = False
        # ha a selecten nem valasztott a juzer mas lokaciot, akkor annak feliratabol kell decryptelni
        if ':' in location:
            locationname = location.split(":")[1].strip()
            locationquery = exec_return("SELECT Id FROM Settlements WHERE name = :locationname", [locationname])
            location = locationquery[1][0][0]
        # uploads folderbe mentése a kepnek
        if correct:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # kep feltoltese az adatbazisba, kategoria megadasa
            exec_noreturn(
                "INSERT INTO Pictures VALUES (:filename, :nick, :title, :description, :location)",
                [filename, nick, title, description, location])
            exec_noreturn("INSERT INTO Categories VALUES (:category, :filename)", [category, filename])
    else:
        flash("Az érvényes fájltípusok: png, jpg, jpeg, gif. ")


# feltoltott kép jelenjen meg html-ben
@app.route('/uploadpic/<filename>')
def send_image(filename):
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    return send_from_directory("uploads", filename)


# modositas gombra nyomva
@app.route('/modifypic', methods=['GET', 'POST'])
def modifypic():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    source = request.args.get('from').strip()
    # formok kezelese
    if request.method == 'POST':
        form_data = request.form  # bekerjuk a formok adatait
        title = form_data.get('title')
        description = form_data.get('description')
        location = form_data.get('location')
        category = form_data.get('category')
        filename = form_data.get('filename')
        # frissites az adatbazisban
        exec_noreturn("""Update Pictures\
                        SET Title = :title, Description = :description, Location = :location\
                        WHERE Filename = :filename""", [title, description, location, filename])
        exec_noreturn("UPDATE Categories SET Name = :category WHERE Pictureid = :filename", [category, filename])
    return redirect(source)


# torles gombra nyomva
@app.route('/delete')
def delete():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    photo = request.args.get('photo')
    source = request.args.get('from').strip()
    exec_noreturn("DELETE FROM Pictures WHERE Filename = :photo", [photo])
    # torlodik a kep, a delete_from_category trigger torli a kategoriak tablabol is
    # nem marad mas hatra, mint hogy reloadoljuk az oldalt, amin vagyunk
    return redirect(source)


@app.route('/rate/<filename>/<score>')
def send_rating(filename, score):
    author = session.get('nick')
    # rate-el ellenőrizzük, hogy az értékelésünkkel ne vegezzünk felesleges Update-lést
    rate = exec_return("SELECT Stars FROM Ratings WHERE Picture=:picture AND Usernick=:author", [filename, author])
    if len(rate[1]) == 0:
        # kep ertekeles feltoltese adatbazisba ha még nincsen
        exec_noreturn("INSERT INTO Ratings VALUES (:star, :picture, :author)", [score, filename, author])
    elif rate[1][0][0] == score:
        pass
    else:
        exec_noreturn("UPDATE Ratings SET Stars=:star WHERE Picture=:picture AND Usernick=:author ",
                      [score, filename, author])
    return redirect(url_for('pictures'))


# képeink oldal tartalma
@app.route('/pictures')
def get_images():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    atlagok = dict()
    # az adatbázisban lévő képek kilistázása filename szerint visszafele rendezve (legujabb lesz az elso)
    images_database = exec_return("SELECT Filename, Title, Description FROM Pictures ORDER BY Filename DESC ")[1]
    for image in images_database:
        atlagok.update({image[0]: avgRate(str(image[0]))})
    return render_template("pictures.html", image_names=images_database, atlagok=atlagok)


@app.route('/pictures/<filename>')
def avgRate(filename):
    atlagok = exec_return("select AVG(stars) from Ratings where picture=:pic", [filename])
    return str(atlagok[1][0][0])


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
        photos_from_category = exec_return("""SELECT Filename, Title, Description,\
                                                (SELECT AVG(Stars) FROM Ratings WHERE Picture=Filename) Avgstars
                                                FROM Pictures, Categories\
                                                WHERE Filename = Pictureid AND Pictureid IN\
                                                (SELECT Pictureid FROM Categories WHERE Name = :chosencategory)\
                                                Order by Avgstars DESC """,
                                           [chosencategory])[1]
        chosen_category_count = exec_return("SELECT COUNT(*) FROM Categories WHERE Name = :chosencategory",
                                            [chosencategory])[1][0][0]
    return render_template('categories.html', categories=CATEGORIES, chosencategory=chosencategory,
                           chosencategorycount=chosen_category_count, photos=photos_from_category)


# mostactive.html
@app.route('/mostactive')
def mostactive():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    # parameterben kapott felhasznalo
    chosenuser = request.args.get('user')
    chosen_user_count = 0
    photos_from_user = []
    # a 8 legtobb keppel rendelkezo felhasznalo
    # a belso select lekeri az osszeset sorrendben, a kulso select limitalja az elso 8-ra
    # azert nyolcra, mert kovetjuk a feng shuit. Na meg ennyi meg nem tulzottan hosszu lista
    topusers = exec_return("""SELECT * FROM (\
                                    SELECT Nick, COUNT(*) FROM Pictures, Users\
                                    WHERE Author = Nick GROUP BY Nick ORDER BY COUNT(*) DESC, Nick\
                                ) WHERE rownum <= 8""")[1]
    if chosenuser is not None:
        photos_from_user = exec_return("""SELECT Filename, Title, Description FROM Pictures\
                                            WHERE Author = :chosenuser""", [chosenuser])[1]
        chosen_user_count = exec_return("SELECT COUNT(*) FROM Pictures where Author = :chosenuser",
                                        [chosenuser])[1][0][0]
    return render_template('mostactive.html', chosenuser=chosenuser, chosenusercount=chosen_user_count,
                           topusers=topusers, photos=photos_from_user)


# worldmap.html
@app.route('/worldmap')
def worldmap():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    settlements = get_settlements()
    # ha mar valasztottunk telepulest, jelenitsuk meg a kepeket
    chosensettlement = request.args.get('place')
    photos_from_place = []
    settlement_faces = []
    # legnepszerubb uticelok feature
    # print(exec_return("""SELECT * FROM TABLE("travelers_places"())""")) # beepitett fuggveny, de nem mukodik
    travelers_places = exec_return("""select Author, Settlements.Name from Pictures, Users, Settlements\
                    where author = users.nick and pictures.location != users.location\
                    and pictures.location = settlements.id ORDER BY Settlements.Name""")[1]
    # dictionarybe rendezzuk {telepules: latogatok} formaban
    mostvisited = dict()
    for elem in travelers_places:
        if elem[1] not in mostvisited.keys():
            mostvisited[elem[1]] = 1
        else:
            mostvisited[elem[1]] += 1
    # sorba rendezzuk a dictionary elemeit ertek szerint, eredmeny egy list
    mostvisited = sorted(mostvisited.items(), key=lambda x: x[1], reverse=True)
    # ha valasztottunk telepulest, jelenitsunk meg kepeket es a varosok arcait
    if chosensettlement is not None:
        photos_from_place = exec_return("""SELECT Filename, Title, Description FROM Pictures\
                                            WHERE Location = :chosensettlement""", [chosensettlement])[1]
        # varosok arcai feature
        settlement_faces = exec_return("""SELECT Author, COUNT(*) FROM Pictures\
                                            WHERE Location = :chosensettlement\
                                            GROUP BY Author ORDER BY COUNT(*), Author""",
                                       [chosensettlement])[1]
        # mostmar a neve kell a telepulesnek az id helyett
        chosensettlement = exec_return("SELECT Name FROM Settlements WHERE Id = :chosensettlement",
                                       [chosensettlement])[1][0][0]
    return render_template('worldmap.html', settlements=settlements, chosensettlement=chosensettlement,
                           mostvisited=mostvisited, photos=photos_from_place, settlement_faces=settlement_faces)


# stats.html
@app.route('/stats')
def stats():
    # ha nem vagyunk bejelentkezve, akkor irany bejelentkezni
    if 'nick' not in session:
        return redirect(url_for('index'))
    # beepitett fgv-k mint: hany kep van feltoltve, ennek hany szazaleka a bejelentkezett usertol, milyen kategoriak
    # kepek hany szazalekat toltotte fol a user a szulovarosaban
    # atlagban milyen ratinget ad, milyet kap
    return render_template('stats.html')


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
