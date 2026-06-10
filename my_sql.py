import pymysql


class MySQLHandler:
    def __init__(self, host, port, user, password, database,charset = 'utf8mb4'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset
            )
            self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            print("成功连接到MySQL数据库")
        except pymysql.Error as e:
            print(f"连接数据库时出错: {e}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("成功断开与MySQL数据库的连接")

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result
        except pymysql.err.OperationalError as e:
            if e.args[0] == 2006 or e.args[0] == 2013:  # 错误码 2006 表示 MySQL server has gone away
                print("捕获到 MySQL server has gone away 异常，尝试重新连接...")
                self.connect()
                self.cursor.execute(query, params)
                result = self.cursor.fetchall()
                return result
            else:
                print(f"发生其他操作错误: {e}")

        except pymysql.Error as e:
            print(f"执行查询时出错: {e}")
            return None

    def execute_update(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.rowcount
        except pymysql.err.OperationalError as e:
            if e.args[0] == 2006 or e.args[0] == 2013:  # 错误码 2006 表示 MySQL server has gone away
                print("捕获到 MySQL server has gone away 异常，尝试重新连接...")
                self.connect()
                self.cursor.execute(query, params)
                self.connection.commit()
                return self.cursor.rowcount
            else:
                print(f"发生其他操作错误: {e}")
        except pymysql.Error as e:
            print(f"执行更新操作时出错: {e}")
            self.connection.rollback()
            return 0

    def insert(self, table, data):
        columns = '`'+'`, `'.join(data.keys())+'`'
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_update(query, tuple(data.values()))

    def update(self, table, data, condition):
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        return self.execute_update(query, tuple(data.values()))

    def delete(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"
        return self.execute_update(query)
    def count(self, table, condition):
        query = f"SELECT COUNT(*) FROM {table} WHERE {condition}"
        result = self.execute_query(query)
        if result:
            return result[0]['COUNT(*)']
        else:
            return 0

