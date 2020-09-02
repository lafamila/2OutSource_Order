from flask import Blueprint, render_template, abort, session, redirect, request, jsonify
from util import DB, loginCheck, SECRET_KEY

fp = Blueprint('function', __name__, url_prefix='/ajax')
fp.secret_key = SECRET_KEY

db = DB(host='localhost', user='root', password='P@ssw0rd', db='order')



@fp.route("/login", methods=['POST'])
def login():
    u_id = request.form.get('u_id')
    u_pw = request.form.get('u_pw')
    print(u_id)
    print(u_pw)
    result = db("SELECT * FROM user WHERE U_ID=%s AND U_PW=%s", (u_id, u_pw))
    if result:
        session['u_sn'] = result[0]['u_sn']
        return jsonify({'result': 1})
    else:
        return jsonify({'result': 0})


@fp.route("/logout", methods=['POST'])
def logout():
    del session['u_sn']
    return jsonify({'result': 1})


@fp.route("/join", methods=['POST'])
def join():
    u_id = request.form.get('u_id')
    u_pw = request.form.get('u_pw')
    u_nm = request.form.get('u_nm')
    result = db("SELECT * FROM user WHERE U_ID=%s", (u_id))
    if result:
        return jsonify({'result': 0, 'msg': '존재하는 아이디입니다.'})
    try:
        u_sn = db("INSERT INTO user SET U_ID=%s, U_PW=%s, U_NM=%s", (u_id, u_pw, u_nm))
        session['u_sn'] = u_sn
        return jsonify({'result': 1})
    except Exception as e:
        return jsonify({'result': 0, 'msg': str(e)})
