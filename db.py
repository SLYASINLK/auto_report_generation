import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "admin",
    "database": "site_selection"
}

TABLE_NAME = "task_information"

def get_connection():
    return pymysql.connect(**DB_CONFIG)
