from flask import Flask, render_template
from db_actions import exec

app = Flask(__name__)


# index.html
@app.route('/')
def index():
    data = exec("SELECT * FROM Countries")
    return render_template('index.html', colnames=data[0], rows=data[1])


if __name__ == "__main__":
    app.run(debug=True)
