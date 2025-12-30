
import sqlite3

try:
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, is_active FROM tools")
    tools = cursor.fetchall()
    
    print(f"Found {len(tools)} tools.")
    for name, is_active in tools:
        print(f"Tool: {name}, Active: {is_active}")

    conn.close()
except Exception as e:
    print(f"DB Error: {e}")
