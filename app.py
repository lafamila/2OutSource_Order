from flask import Flask
from views.templates import bp
from views.functions import fp
from views.admin import ap
from util import DB, SECRET_KEY, PW

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(ap)
app.register_blueprint(bp)
app.register_blueprint(fp)

db = DB(host='localhost', user='root', password=PW, db='order')

if __name__ == "__main__":
    app.run(debug=True)