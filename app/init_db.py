import urllib

url = 'mysql+mysqlconnector://root@localhost/evaluatex'

DATABASE_PASSWORD = 'test'
# SqlAlchemy Database Configuration With Mysql
DATABASE_PASSWORD_UPDATED = urllib.parse.quote_plus(DATABASE_PASSWORD)
url = 'mysql+pymysql://user:'+DATABASE_PASSWORD_UPDATED+'@db/evaluatex'

'''
DATABASE_PASSWORD = 'cossmic..'
DATABASE_PASSWORD_UPDATED = urllib.parse.quote_plus(DATABASE_PASSWORD)
url = 'mysql+pymysql://root:'+DATABASE_PASSWORD_UPDATED+'@localhost/evaluate20230615'
'''
