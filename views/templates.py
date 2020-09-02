from flask import Blueprint, render_template, abort, session, redirect, request
from util import DB, loginCheck, SECRET_KEY

bp = Blueprint('template', __name__, url_prefix='/')
bp.secret_key = SECRET_KEY

db = DB(host='localhost', user='root', password='P@ssw0rd', db='order')



#Index 페이지를 위한 url route
@bp.route("/")
@bp.route("/<menu_name>")
def render(menu_name=''):
    menu_list = db("SELECT * FROM menu ORDER BY MENU_SN")
    isLogin = loginCheck(session)
    if menu_name == '':
        return render_template('index.html', menu='', menuList=menu_list, isLogin=isLogin)

    isMenu = False
    for m in menu_list:
        if m['menu_name'] == menu_name:
            isMenu = True

    if isMenu:
        if isLogin:
            return render_template('{}.html'.format(menu_name), menu=menu_name, menuList=menu_list, isLogin=isLogin)
        else:
            return redirect('/login?menu={}'.format(menu_name))
    else:
        abort(404)

@bp.route("/login")
def login():
    menu = request.args.get('menu')
    isLogin = loginCheck(session)
    if isLogin:
        return redirect('/')
    if menu:
        return render_template('login.html', menu=menu)
    else:
        return render_template('login.html', menu='')