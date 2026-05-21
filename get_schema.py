import os
import django
import sys
import json

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_system.settings')
django.setup()

from django.db import connection

def get_db_structure():
    structure = {}
    with connection.cursor() as cursor:
        # Get tables in 'Производство' schema
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'Производство'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'Производство' AND TABLE_NAME = '{table}'
            """)
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    'name': col[0],
                    'type': col[1],
                    'max_length': col[2],
                    'nullable': col[3] == 'YES'
                })
            structure[table] = columns
            
    return structure

if __name__ == "__main__":
    try:
        data = get_db_structure()
        with open('db_structure.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Structure saved to db_structure.json")
    except Exception as e:
        print(f"Error: {e}")
