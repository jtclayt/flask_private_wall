from pymysql import cursors, connect


class MySQLConnections:
  def __init__(self, db):
    # establish connection to db
    self.connection = connect(
      host='localhost',
      user='root',
      password='root',
      db=db,
      charset='utf8mb4',
      cursorclass=cursors.DictCursor,
      autocommit=True
    )

  def query_db(self, query, data=None):
    with self.connection.cursor() as cursor:
      try:
        query = cursor.mogrify(query, data)
        print('Running query:', query)
        executable = cursor.execute(query, data)
        if query.lower().find('insert') >= 0:
          self.connection.commit()
          return cursor.lastrowid
        elif query.lower().find('select') >= 0:
          return cursor.fetchall()
        else:
          self.connection.commit()
      except Exception as e:
        print('Exception raised:', e)
        return False
      finally:
        # close the db connection
        self.connection.close()

def connectToMySQL(db):
  return MySQLConnections(db)
