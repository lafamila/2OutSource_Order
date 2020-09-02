import pymysql
import datetime

SECRET_KEY = 'hello,python'

def loginCheck(session):
    return 'u_sn' in session

class Cursor:
    def __init__(self, cursor):
        self.cursor = cursor

class DB:
    RESULT_EXIST = 0
    RESULT_EXIST_ID = 1
    RESULT_NOT_EXIST = 2

    def __init__(self, host, user, password, db, port=3306):
        self._conn = pymysql.connect(host, user, password, db, port=port)

    def _cursor(self):
        return self._conn.cursor(pymysql.cursors.DictCursor)

    def _getValue(self, value):
        if type(value) is datetime.datetime:
            return str(value)
        else:
            return value

    def _getResult(self, resultSet):
        _resultSet = []
        for result in resultSet:
            _keys = result.keys()
            _result = dict()
            for key in _keys:
                value = self._getValue(result[key])
                _result[key.lower()] = value
            _resultSet.append(_result)
        return _resultSet

    def _getQueryType(self, sql):
        _sql = sql.upper()
        if _sql.startswith('SELECT'):
            return DB.RESULT_EXIST
        elif _sql.startswith('INSERT'):
            return DB.RESULT_EXIST_ID
        else:
            return DB.RESULT_NOT_EXIST

    def __call__(self, sql, params=None):
        _curs = self._cursor()
        if params:
            _curs.execute(sql, params)
        else:
            _curs.execute(sql)
        if self._getQueryType(sql) is DB.RESULT_EXIST:
            _result = _curs.fetchall()
            return self._getResult(_result)
        elif self._getQueryType(sql) is DB.RESULT_EXIST_ID:
            _rowId = _curs.lastrowid
            self._conn.commit()
            return _rowId
        else:
            self._conn.commit()
            return None

