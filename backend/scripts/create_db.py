import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # Connect to default 'postgres' database to create the new one
        con = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            host="localhost",
            password="123",
            port="5432"
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'ai_counsellor'")
        exists = cur.fetchone()
        
        if not exists:
            print("Creating database 'ai_counsellor'...")
            cur.execute("CREATE DATABASE ai_counsellor")
            print("Database created.")
        else:
            print("Database 'ai_counsellor' already exists.")
            
        cur.close()
        con.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
