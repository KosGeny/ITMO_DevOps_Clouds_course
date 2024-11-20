import os;
import mysql.connector;

db_config = {
    "host": os.getenv("MYSQL_HOST", ""),
    "user": os.getenv("MYSQL_USER", ""),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_NAME", "")
}

try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to MySQL database")

except mysql.connector.Error:
    print("Error while connecting to MySQL database")
