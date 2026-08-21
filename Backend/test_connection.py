from database import engine

try:
    connection = engine.connect()
    print("✅ MySQL database connected successfully!")
    connection.close()

except Exception as e:
    print("❌ Connection failed!")
    print(e)