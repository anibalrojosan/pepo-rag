import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()
        
        # SQL query to verify if the vector extension is available
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        extension_exists = cur.fetchone()
        
        if extension_exists:
            print("✅ Connection successful, 'pgvector' extension detected.")
        else:
            # Attempt to create it if it doesn't exist (requires superuser)
            print("⚠️ Connection successful. 'pgvector' is not active. Attempting to activate...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("✅ 'pgvector' extension activated successfully.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error connecting to the database: {e}")

if __name__ == "__main__":
    test_connection()