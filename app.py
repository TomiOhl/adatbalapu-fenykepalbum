from flask import Flask, render_template, request, url_for, redirect
from db_actions import exec

app = Flask(__name__)


# index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ha benne van a juzer az adatbazisban
        return redirect(url_for('profile'))
    return render_template('index.html')


# profile.html
@app.route('/profile')
def profile():
    data = exec("SELECT * FROM Countries")
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
