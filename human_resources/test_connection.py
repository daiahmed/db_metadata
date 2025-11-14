import oracledb

username = "system"
password = "SysPassword1"
dsn = "localhost:8521/freepdb1"

try:
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    print("✅ Successfully connected to Oracle Database!")
except oracledb.DatabaseError as e:
    print("❌ Connection failed:", e)
