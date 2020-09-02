from flask import Flask
from views.templates import bp
from views.functions import fp
from util import DB, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(bp)
app.register_blueprint(fp)


db = DB(host='localhost', user='root', password='P@ssw0rd', db='order')

if __name__ == "__main__":
    app.run(debug=True)