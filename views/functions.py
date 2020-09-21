from flask import Blueprint, render_template, abort, session, redirect, request, jsonify, url_for, send_file
from util import DB, loginCheck, SECRET_KEY, getToday, PW
import datetime
import random

fp = Blueprint('function', __name__, url_prefix='/ajax')
fp.secret_key = SECRET_KEY

db = DB(host='localhost', user='root', password=PW, db='order')



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
    u_cp = request.form.get('u_cp')
    result = db("SELECT * FROM user WHERE U_ID=%s", (u_id))
    if result:
        return jsonify({'result': 0, 'msg': '존재하는 아이디입니다.'})
    try:
        u_sn = db("INSERT INTO user(U_ID, U_PW, U_NM, U_CP) VALUES (%s, %s, %s, %s)", (u_id, u_pw, u_nm, u_cp))
        brands = db("SELECT BRND_SN FROM brand")
        for brand in brands:
            db("INSERT INTO user_brand(U_SN, BRND_SN, BRND_PATH, BRND_VIP) VALUES (%s, %s, 1, 0)", (u_sn, brand["brnd_sn"]))
        session['u_sn'] = u_sn
        return jsonify({'result': 1})
    except Exception as e:
        return jsonify({'result': 0, 'msg': str(e)})


@fp.route('/update', methods=['POST'])
def update():
    table = request.form.get('table')
    col = request.form.get('col')
    sn = request.form.get('sn')
    data = request.form.get('data')
    col_sn = request.form.get('stand')
    db("UPDATE {} SET {}=%s WHERE {}=%s".format(table, col, col_sn), (data, sn))

    return jsonify({"result" : 1, "msg" : "성공적으로 수정되었습니다."})

@fp.route('/updateMulti', methods=['POST'])
def updateMulti():
    tables = request.form.getlist('table[]')
    cols = request.form.getlist('col[]')
    sns = request.form.getlist('sn[]')
    datas = request.form.getlist('data[]')
    col_sns = request.form.getlist('stand[]')
    for table, col, sn, data, col_sn in zip(tables, cols, sns, datas, col_sns):
        db("UPDATE {} SET {}=%s WHERE {}=%s".format(table, col, col_sn), (data, sn))

    return jsonify({"result" : 1, "msg" : "성공적으로 수정되었습니다."})\

@fp.route('/delete', methods=['POST'])
def delete():
    table = request.form.get('table')
    col = request.form.get('col')
    sn = request.form.get('sn')
    db("DELETE FROM {} WHERE {}=%s".format(table, col), (sn))

    return jsonify({"result" : 1, "msg" : "성공적으로 삭제되었습니다."})

@fp.route('/insertBrand', methods=['POST'])
def insertBrand():
    brand = request.form.get("brand")
    day = request.form.get("day")
    today = getToday(time=True)

    sn = db("INSERT INTO brand(BRND_NM, BRND_DAY, BRND_PATH, BRND_VIP, REGIST_DTM) VALUES (%s, %s, NULL, NULL, %s)", (brand, day, today))
    users = db("SELECT U_SN FROM user")
    for user in users:
        db("INSERT INTO user_brand(U_SN, BRND_SN, BRND_PATH, BRND_VIP) VALUES (%s, %s, 1, 0)", (user["u_sn"], sn))

    return jsonify({"result" : 1})

@fp.route('/getBrands')
def getBrands():
    page = int(request.args.get("page"))

    result = db("SELECT * FROM brand WHERE 1 ORDER BY REGIST_DTM LIMIT %s OFFSET %s", (10, page*10))
    count = db("SELECT * FROM brand WHERE 1")

    return jsonify({"data" : result, "recordsTotal" : len(count)})

@fp.route('/getAllBrands')
def getAllBrands():
    u_sn = int(request.args.get("u_sn"))
    if u_sn == 0:
        if "u_sn" in session:
            u_sn = session['u_sn']
            print(u_sn)
            result = db("SELECT b.*, ub.UB_SN, ub.U_SN, ub.BRND_PATH as PATH, ub.BRND_VIP as VIP FROM brand b RIGHT JOIN user_brand ub ON b.BRND_SN=ub.BRND_SN WHERE ub.U_SN=%s ORDER BY b.REGIST_DTM", u_sn)
        else:
            return jsonify({"result" : 0})
    else:
        result = db("SELECT b.*, ub.UB_SN, ub.U_SN, ub.BRND_PATH as PATH, ub.BRND_VIP as VIP FROM brand b RIGHT JOIN user_brand ub ON b.BRND_SN=ub.BRND_SN WHERE ub.U_SN=%s ORDER BY b.REGIST_DTM", u_sn)
    return jsonify({"data" : result})

@fp.route('/uploadBrandFile', methods=['POST'])
def uploadBrandFile():
    sn = request.form.get("sn")
    file_type = request.form.get("type")
    u_file = request.files.get('file')

    origin = u_file.filename
    name, ext = origin.split(".")
    path = './static/files/{}_{}.{}'.format(name, datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S"), ext)
    u_file.save(path)

    if int(file_type) == 0:
        db("UPDATE brand SET BRND_PATH=%s WHERE BRND_SN=%s", (path, sn))
    else:
        db("UPDATE brand SET BRND_VIP=%s WHERE BRND_SN=%s", (path, sn))
    return jsonify({"result" : 1, "msg" : "업로드되었습니다."})


@fp.route('/downloadFile', methods=['POST'])
def downloadFile():
    sn = request.form.get("sn")
    col = int(request.form.get("col"))
    if col == 0:
        column = "BRND_PATH"
        tag = ""
    else:
        column = "BRND_VIP"
        tag = "_vip"
    result = db("SELECT BRND_NM, {} FROM brand WHERE BRND_SN=%s".format(column), (sn))
    filepath = result[0][column.lower()]
    name = result[0]["brnd_nm"]
    ext = filepath.split(".")[-1]
    return send_file(filepath,
                     mimetype='text/{}'.format(ext),
                     attachment_filename='{}{}.{}'.format(name, tag, ext),# 다운받아지는 파일 이름.
                     as_attachment=True)


@fp.route('/searchUser', methods=['POST'])
def searchUser():
    cond = int(request.form.get('condition'))
    q = request.form.get('query')
    if cond == 1:
        col = "u.U_ID"
    elif cond == 2:
        col = "u.U_NM"
    elif cond == 3:
        col = "u.U_CP"
    else:
        result = db(
            "SELECT u.*, c.C_REGION, c.C_CHANNEL, c.C_PATH FROM user u LEFT OUTER JOIN (SELECT * FROM cert WHERE C_SN IN (SELECT MAX(C_SN) FROM cert GROUP BY U_SN)) c ON u.U_SN=c.U_SN WHERE {} LIKE %s OR {} LIKE %s OR {} LIKE %s".format(
                'u.U_ID', 'u.U_NM', 'u.U_CP'), ('%{}%'.format(q), '%{}%'.format(q), '%{}%'.format(q)))
        if len(result) > 0:
            return jsonify({"result": 1, "data": result})
        else:
            return jsonify({"result": 0})

    result = db("SELECT u.*, c.C_REGION, c.C_CHANNEL, c.C_PATH FROM user u LEFT OUTER JOIN (SELECT * FROM cert WHERE C_SN IN (SELECT MAX(C_SN) FROM cert GROUP BY U_SN)) c ON u.U_SN=c.U_SN WHERE {} LIKE %s".format(col), '%{}%'.format(q))
    if len(result) > 0:
        return jsonify({"result" : 1, "data" : result})
    else:
        return jsonify({"result" : 0})

@fp.route('/getSchedule', methods=['POST'])
def getSchedule():
    result = {}
    data = db("SELECT * FROM brand ORDER BY BRND_DAY")

    for d in data:
        day = d["brnd_day"]
        if day in result:
            result[day].append({"name": d["brnd_nm"], "brnd_sn": d["brnd_sn"]})
        else:
            result[day] = [{"name": d["brnd_nm"], "brnd_sn": d["brnd_sn"]}]
    return jsonify(result)

@fp.route('/getStatus', methods=['POST'])
def getStatus():
    data = db("SELECT * FROM code WHERE CODE_NM='O_STTUS' ORDER BY CODE")

    return jsonify(data)

@fp.route('/getArticleType', methods=['POST'])
def getArticleType():
    data = db("SELECT * FROM code WHERE CODE_NM='A_TYPE' ORDER BY CODE")

    return jsonify(data)


@fp.route('/uploadBrand', methods=['POST'])
def uploadBrand():
    if "u_sn" in session:
        u_sn = session['u_sn']
        sn = request.form.get("sn")
        u_file = request.files.get('file')

        origin = u_file.filename
        name, ext = origin.split(".")
        path = './static/files/{}_{}.{}'.format(name, datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S"), ext)
        u_file.save(path)

        o_sns = db("SELECT O_SN FROM ordered")
        ordered = [o_sn["o_sn"] for o_sn in o_sns]
        order = str(random.randint(1, 10000000)).zfill(7)
        while order in ordered:
            order = str(random.randint(1, 10000000)).zfill(7)

        # 만약 예정일 자동계산이 아니면 db table NULL 가능으로 바꾸고 기본값 NULL 추가한다음
        # db("INSERT ordered(O_SN, U_SN, BRND_SN, O_PATH, REGIST_DTM) VALUES (%s, %s, %s, %s, %s, %s)", (order, u_sn, sn,  path, getToday(time=True)))

        now = getToday(time=True)
        db("INSERT ordered(O_SN, U_SN, BRND_SN, O_DAY, O_PATH, REGIST_DTM) VALUES (%s, %s, %s, %s, %s, %s)", (order, u_sn, sn, getToday(delta=-3), path, now))
        db("INSERT status(O_SN, O_STTUS, REGIST_DTM) VALUES (%s, %s, %s)", (order, 0, now))
        return jsonify({"result" : 1, "msg" : "주문번호 : {} \n업로드되었습니다.".format(order)})
    else:
        return jsonify({"result" : 0, "msg" : "로그인이 필요합니다."})


@fp.route('/getBrandLog', methods=['POST'])
def getBrandLog():
    if "u_sn" in session:
        u_sn = session['u_sn']
        data = db("SELECT o.REGIST_DTM, b.BRND_NM FROM ordered o LEFT JOIN brand b ON o.BRND_SN = b.BRND_SN WHERE o.U_SN=%s ORDER BY o.REGIST_DTM", (u_sn))
        return jsonify({"result" : 1, "data" : data})
    else:
        return jsonify({"result" : 0, "msg" : "로그인이 필요합니다."})

@fp.route('/getOrdered')
def getOrdered():
    if "u_sn" in session:
        u_sn = session['u_sn']
        page = int(request.args.get("page"))

        result = db("SELECT o.*, b.BRND_NM, s.O_STTUS, (SELECT CODE_LABEL FROM code WHERE CODE_NM='O_STTUS' AND CODE=s.O_STTUS) AS STTUS, s.REGIST_DTM AS STTUS_DATE FROM ordered o LEFT JOIN brand b ON o.brnd_sn=b.brnd_sn LEFT JOIN (SELECT * FROM status WHERE S_SN IN (SELECT MAX(S_SN) FROM status GROUP BY O_SN)) s ON o.O_SN=s.O_SN WHERE o.U_SN=%s ORDER BY o.REGIST_DTM LIMIT %s OFFSET %s", (u_sn, 10, page*10))
        count = db("SELECT * FROM ordered o WHERE o.U_SN=%s", (u_sn))
        user = db("SELECT * FROM user WHERE U_SN=%s", (u_sn))
        return jsonify({"data" : result, "recordsTotal" : len(count), "user" : user[0]})
    else:
        return jsonify({"data" : [], "recordsTotal" : 0})




@fp.route('/downloadCert', methods=['POST'])
def downloadCert():
    u_sn = request.form.get("u_sn")
    result = db("SELECT u.*, c.C_REGION, c.C_CHANNEL, c.C_PATH FROM user u LEFT OUTER JOIN (SELECT * FROM cert WHERE C_SN IN (SELECT MAX(C_SN) FROM cert GROUP BY U_SN)) c ON u.U_SN=c.U_SN WHERE u.U_SN=%s", u_sn)
    filepath = result[0]['c_path']
    name = result[0]["u_nm"]
    tag = result[0]["c_region"]+"_"+result[0]["c_channel"]
    ext = filepath.split(".")[-1]
    return send_file(filepath,
                     mimetype='text/{}'.format(ext),
                     attachment_filename='{}_{}.{}'.format(name, tag, ext),# 다운받아지는 파일 이름.
                     as_attachment=True)

@fp.route('/uploadCert', methods=['POST'])
def uploadCert():
    u_sn = session["u_sn"]
    c_region = request.form.get("c_region")
    c_channel = request.form.get("c_channel")
    u_file = request.files.get('file')

    origin = u_file.filename
    name, ext = origin.split(".")
    path = './static/files/{}_{}.{}'.format(name, datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S"), ext)
    u_file.save(path)
    db("INSERT INTO cert(U_SN, C_REGION, C_CHANNEL, C_PATH) VALUES (%s, %s, %s, %s)", (u_sn, c_region, c_channel, path))
    return "<script>alert('접수되었습니다.');close();</script>"

@fp.route('/getSearchOrdered')
def getSearchOrdered():

    statuslist = db("SELECT CODE_LABEL AS LABEL, CODE AS VALUE FROM code WHERE CODE_NM='O_STTUS' ORDER BY CODE")


    where = ""
    params = []


    page = int(request.args.get("page"))

    queryType = int(request.args.get("queryType"))
    queries = request.args.getlist("queries[]")

    dateType = int(request.args.get("dateType"))
    start = request.args.get("start")
    end = request.args.get("end")

    brand = int(request.args.get("brand"))

    status = request.args.getlist("status[]")

    if len(queries) > 0:
        column = ''
        if queryType == 1:
            column = "o.O_SN"
        elif queryType == 2:
            column = "u.U_ID"
        else:
            column = "u.U_CP"
        where += " AND {} IN ({}) ".format(column, ','.join(['%s']*len(queries)))
        params += queries

    if dateType == 1:
        column = "o.REGIST_DTM"
    elif dateType == 2:
        column = "o.O_DAY"
    else:
        column = "o.O_DELI"
    where += " AND {} BETWEEN %s AND %s ".format(column)
    params += ["{} 00:00:00".format(start), "{} 23:59:59".format(end)]

    if brand > 0:
        where += " AND b.BRND_SN = %s "
        params.append(brand)

    if len(status) > 0:
        where += " AND s.O_STTUS IN ({})".format(','.join(['%s']*len(status)))
        params += status
    else:
        return jsonify({"data": [], "recordsTotal": 0, "status": statuslist})


    query = "SELECT o.*, u.U_NM, u.U_ID, u.U_CP, b.BRND_SN, b.BRND_NM, s.O_STTUS, (SELECT CODE_LABEL FROM code WHERE CODE_NM='O_STTUS' AND CODE=s.O_STTUS) AS STTUS, s.REGIST_DTM AS STTUS_DATE FROM ordered o LEFT JOIN brand b ON o.brnd_sn=b.brnd_sn LEFT JOIN user u ON o.U_SN=u.U_SN LEFT JOIN (SELECT * FROM status WHERE S_SN IN (SELECT MAX(S_SN) FROM status GROUP BY O_SN)) s ON o.O_SN=s.O_SN WHERE 1=1 {} ORDER BY o.REGIST_DTM".format(where)
    result = db(query+" LIMIT %s OFFSET %s", tuple(params+[10, page*10]))
    count = db(query, tuple(params))
    return jsonify({"data" : result, "recordsTotal" : len(count), "status" : statuslist})

@fp.route('/insertStatus', methods=['POST'])
def insertStatus():
    o_sn = request.form.get("o_sn")
    data = request.form.get("data")
    now = getToday(time=True)
    db("INSERT INTO status(O_SN, O_STTUS, REGIST_DTM) VALUES (%s, %s, %s)", (o_sn, data, now))
    return jsonify({"result" : 1, "msg" : "성공적으로 수정되었습니다."})


@fp.route('/downloadOrdered', methods=['POST'])
def downloadOrdered():
    sn = request.form.get("sn")
    result = db("SELECT o.O_PATH, o.U_SN, u.U_ID FROM ordered o LEFT JOIN user u ON u.U_SN=o.U_SN WHERE o.O_SN=%s", (sn))
    filepath = result[0]['o_path']
    name = result[0]["u_id"]
    ext = filepath.split(".")[-1]
    return send_file(filepath,
                     mimetype='text/{}'.format(ext),
                     attachment_filename='{}_{}.{}'.format(name, sn, ext),# 다운받아지는 파일 이름.
                     as_attachment=True)

@fp.route('/uploadConfirm', methods=['POST'])
def uploadConfirm():
    sn = request.form.get("sn")
    u_file = request.files.get('file')

    origin = u_file.filename
    name, ext = origin.split(".")
    path = './static/files/{}_{}.{}'.format(name, datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S"), ext)
    u_file.save(path)

    db("UPDATE ordered SET O_CONFIRM_PATH=%s WHERE O_SN=%s", (path, sn))
    return jsonify({"result" : 1, "msg" : "업로드되었습니다."})


@fp.route('/downloadConfirm', methods=['POST'])
def downloadConfirm():
    sn = request.form.get("sn")
    result = db("SELECT o.O_CONFIRM_PATH, o.U_SN, u.U_ID FROM ordered o LEFT JOIN user u ON u.U_SN=o.U_SN WHERE o.O_SN=%s", (sn))
    filepath = result[0]['o_confirm_path']
    name = result[0]["u_id"]
    ext = filepath.split(".")[-1]
    return send_file(filepath,
                     mimetype='text/{}'.format(ext),
                     attachment_filename='{}_{}.{}'.format(name, sn, ext),# 다운받아지는 파일 이름.
                     as_attachment=True)


@fp.route('/getArticle')
def getArticle():
    page = int(request.args.get("page"))

    result = db("SELECT a.*, u.U_ID, c.A_SN AS CNNC, (SELECT CODE_LABEL FROM code WHERE CODE_NM='A_TYPE' AND CODE=a.A_TYPE) AS TYPE FROM article a LEFT JOIN user u ON a.U_SN=u.U_SN LEFT OUTER JOIN article c ON c.A_CNNC=a.A_SN WHERE a.A_CNNC IS NULL ORDER BY a.REGIST_DTM LIMIT %s OFFSET %s", (10, page*10))
    count = db("SELECT * FROM article WHERE A_CNNC IS NULL")

    return jsonify({"data" : result, "recordsTotal" : len(count)})

@fp.route('/getOnlyArticle')
def getOnlyArticle():
    where = ""
    params = []


    page = int(request.args.get("page"))

    # queryType = int(request.args.get("queryType"))
    # queries = request.args.getlist("queries[]")

    start = request.args.get("start")
    end = request.args.get("end")
    where += " AND a.REGIST_DTM BETWEEN %s AND %s "
    params += ["{} 00:00:00".format(start), "{} 23:59:59".format(end)]

    articleType = int(request.args.get("articleType"))
    if articleType > 0:
        where += " AND a.A_TYPE=%s "
        params.append(articleType)


    status = int(request.args.get("status"))
    if status == 1:
        where += " AND a.A_TYPE > 0 AND c.A_SN IS NULL "
    elif status == 2:
        where += " AND a.A_TYPE > 0 AND c.A_SN IS NOT NULL "
    else:
        where += " AND a.A_TYPE > 0 "

    # if len(queries) > 0:
    #     column = ''
    #     if queryType == 1:
    #         column = "o.O_SN"
    #     elif queryType == 2:
    #         column = "u.U_ID"
    #     else:
    #         column = "u.U_CP"
    #     where += " AND {} IN ({}) ".format(column, ','.join(['%s']*len(queries)))
    #     params += queries





    query = "SELECT a.*, u.U_ID, c.A_SN AS CNNC, (SELECT CODE_LABEL FROM code WHERE CODE_NM='A_TYPE' AND CODE=a.A_TYPE) AS TYPE FROM article a LEFT JOIN user u ON a.U_SN=u.U_SN LEFT OUTER JOIN article c ON c.A_CNNC=a.A_SN WHERE 1=1 {} ORDER BY a.REGIST_DTM".format(where)
    result = db(query+" LIMIT %s OFFSET %s", tuple(params+[10, page*10]))
    count = db(query, tuple(params))
    return jsonify({"data" : result, "recordsTotal" : len(count)})



    return jsonify({"data" : result, "recordsTotal" : len(count)})

@fp.route('/showArticle', methods=['POST'])
def showArticle():
    isLogin = loginCheck(session)
    if isLogin:
        u_sn = session["u_sn"]
        a_sn = request.form.get('a_sn')
        article = db("SELECT a.*, c.U_SN as U_CNNC_SN, c.A_SN AS A_CNNC_SN FROM article a LEFT JOIN article c ON a.A_CNNC=c.A_SN WHERE a.A_SN=%s", a_sn)
        if article[0]["u_sn"] == int(u_sn) or article[0]["u_cnnc_sn"] == int(u_sn):
            return jsonify({'result' : 1, 'data' : article})
        else:
            return jsonify({'result' : 0, 'msg' : "자신이 작성한 게시글만 확인할 수 있습니다."})
    else:
        return jsonify({'result' : -1, 'msg' : "로그인이 필요합니다."})

@fp.route('/insertArticle', methods=['POST'])
def insertArticle():
    if "u_sn" in session:
        u_sn = session["u_sn"]
    else:
        u_sn = 0
    a_type = request.form.get("a_type")
    if a_type is None:
        a_type = 0
    o_sn = request.form.get("o_sn")
    a_title = request.form.get("a_title")
    a_content = request.form.get("a_content")
    a_cnnc = request.form.get("a_sn")
    print(a_cnnc)
    print(a_type)
    now = getToday(time=True)
    db("INSERT INTO article(U_SN, A_TYPE, O_SN, A_TITLE, A_CONTENT, A_CNNC, REGIST_DTM) VALUES (%s, %s, %s, %s, %s, %s, %s)", (u_sn, a_type, o_sn, a_title, a_content, a_cnnc, now))
    return '<script>alert("입력되었습니다.");window.opener.reload(0); close();</script>'



@fp.route('/getAlerts')
def getAlerts():

    where = ""
    where += " AND s.O_STTUS IN (0)"
    query = "SELECT o.*, u.U_NM, u.U_ID, u.U_CP, b.BRND_SN, b.BRND_NM, s.O_STTUS, (SELECT CODE_LABEL FROM code WHERE CODE_NM='O_STTUS' AND CODE=s.O_STTUS) AS STTUS, s.REGIST_DTM AS STTUS_DATE FROM ordered o LEFT JOIN brand b ON o.brnd_sn=b.brnd_sn LEFT JOIN user u ON o.U_SN=u.U_SN LEFT JOIN (SELECT * FROM status WHERE S_SN IN (SELECT MAX(S_SN) FROM status GROUP BY O_SN)) s ON o.O_SN=s.O_SN WHERE 1=1 {} ORDER BY o.REGIST_DTM".format(where)
    ordered = db(query+" LIMIT 3 OFFSET 0")
    orderedCount = len(db(query))

    where = ""
    query = ""
    money = []
    moneyCount = 0

    where = ""
    where += " AND a.A_TYPE > 0 AND c.A_SN IS NULL "
    query = "SELECT a.*, u.U_ID, c.A_SN AS CNNC, (SELECT CODE_LABEL FROM code WHERE CODE_NM='A_TYPE' AND CODE=a.A_TYPE) AS TYPE FROM article a LEFT JOIN user u ON a.U_SN=u.U_SN LEFT OUTER JOIN article c ON c.A_CNNC=a.A_SN WHERE 1=1 {} ORDER BY a.REGIST_DTM".format(where)
    article = db(query+" LIMIT 3 OFFSET 0")
    articleCount = len(db(query))

    return jsonify({"ordered" : ordered, "orderedCount" : orderedCount, "money" : money, "moneyCount": moneyCount, "article" : article, "articleCount" : articleCount})

@fp.route('/insertDetail', methods=['POST'])
def insertDetail():
    data = request.form.get('data')
    now = getToday()
    db("INSERT INTO main(M_TYPE, M_TEXT, REGIST_DTM) VALUES(2, %s, %s)", (data, now))
    return jsonify({"result" : 1})

@fp.route('/getDetail')
def getDetail():
    detail = db("SELECT * FROM main WHERE M_TYPE=2 ORDER BY REGIST_DTM DESC LIMIT 1 OFFSET 0")
    if len(detail) > 0:
        return jsonify({"data" : detail})
    else:
        return jsonify({"data" : []})

@fp.route('/insertMain', methods=['POST'])
def insertMain():
    title = request.form.get('title')
    text = request.form.get('text')
    now = getToday()
    db("INSERT INTO main(M_TYPE, M_TITLE, M_TEXT, REGIST_DTM) VALUES(1, %s, %s, %s)", (title, text, now))
    return jsonify({"result" : 1})

@fp.route('/getMain')
def getMain():
    detail = db("SELECT * FROM main WHERE M_TYPE=1 ORDER BY REGIST_DTM DESC LIMIT 5 OFFSET 0")
    if len(detail) > 0:
        return jsonify({"data" : detail})
    else:
        return jsonify({"data" : []})

@fp.route('/getMainAll')
def getMainAll():

    page = int(request.args.get("page"))

    result = db("SELECT * FROM main WHERE M_TYPE=1 ORDER BY REGIST_DTM LIMIT %s OFFSET %s", (10, page*10))
    count = db("SELECT * FROM main WHERE M_TYPE=1")

    return jsonify({"data" : result, "recordsTotal" : len(count)})
