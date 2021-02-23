db = {
    'user'     : 'admin',
    'password' : 'ewha2020summar',
    'host'     : 'db-summar-server.cpemlh0lctvc.us-east-2.rds.amazonaws.com',
    'port'     : 3306,
    'database' : 'summardb'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"