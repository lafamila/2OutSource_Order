from flask import Blueprint, render_template, abort, session, redirect, request
from util import DB, loginCheck, SECRET_KEY, PW

bp = Blueprint('template', __name__, url_prefix='/')
bp.secret_key = SECRET_KEY

db = DB(host='localhost', user='root', password=PW, db='order')



#Index 페이지를 위한 url route
@bp.route("/")
@bp.route("/<menu_name>")
def render(menu_name=''):
    menu_list = db("SELECT * FROM menu WHERE MENU_USE=1 ORDER BY MENU_ORDR")
    isLogin = loginCheck(session)
    if menu_name == '':
        return render_template('index.html', menu='', menuList=menu_list, isLogin=isLogin)

    isMenu = False
    for m in menu_list:
        if m['menu_name'] == menu_name:
            isMenu = True

    if isMenu:
        if isLogin:
            u_sn = session["u_sn"]
            user = db("SELECT U_ID FROM user WHERE U_SN=%s", (u_sn))
            return render_template('{}.html'.format(menu_name), menu=menu_name, menuList=menu_list, isLogin=isLogin, u_id=user[0]["u_id"])
        else:
            return redirect('/login?menu={}'.format(menu_name))
    else:
        abort(404)

@bp.route("/popup/deposit")
def deposit():
    menu_list = db("SELECT * FROM menu WHERE MENU_USE=1 ORDER BY MENU_ORDR")
    isLogin = loginCheck(session)
    if isLogin:
        u_sn = session["u_sn"]
        user = db("SELECT U_ID FROM user WHERE U_SN=%s", (u_sn))
        return render_template('{}.html'.format('deposit'), menu='ordered', menuList=menu_list, isLogin=isLogin,
                               u_id=user[0]["u_id"])
    else:
        return redirect('/login?menu={}'.format('ordered'))


@bp.route("/popup/foreign")
def foreign():
    isLogin = loginCheck(session)
    if not isLogin:
        return redirect('/login')
    else:
        return render_template("popup/foreign.html")

@bp.route("/popup/ask")
def ask():
    isLogin = loginCheck(session)
    if not isLogin:
        return redirect('/login')
    else:
        u_sn = session["u_sn"]
        options = db("SELECT CODE_LABEL AS LABEL, CODE AS VALUE FROM code WHERE CODE_NM='A_TYPE' ORDER BY CODE")
        ordered = db("SELECT O_SN FROM ordered WHERE U_SN=%s", u_sn)
        return render_template("popup/ask.html", options=options, ordered=ordered)


@bp.route("/popup/showAsk")
def showAsk():
    isLogin = loginCheck(session)
    if not isLogin:
        return redirect('/login')
    else:
        u_sn = session["u_sn"]
        a_sn = request.args.get('a_sn')
        options = db("SELECT CODE_LABEL AS LABEL, CODE AS VALUE FROM code WHERE CODE_NM='A_TYPE' ORDER BY CODE")
        ordered = db("SELECT O_SN FROM ordered WHERE U_SN=%s", u_sn)
        return render_template("popup/show.html", options=options, ordered=ordered)



@bp.route("/login", methods=['GET', 'POST'])
def login():
    menu = request.args.get('menu')
    isLogin = loginCheck(session)
    if isLogin:
        return redirect('/')
    if menu:
        return render_template('login.html', menu=menu)
    else:
        return render_template('login.html', menu='')


@bp.route("/test")
def test():
    menu_list = db("SELECT * FROM menu ORDER BY MENU_SN")
    isLogin = loginCheck(session)
    return render_template('common/header2.html', menu='', menuList=menu_list, isLogin=isLogin)
