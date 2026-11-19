import pyodbc
import pandas as pd

# připojení k databázi
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\MSSQLSERVER01;"
    r"DATABASE=AdventureWorksDW2019;"
    r"Trusted_Connection=yes;"
)

query = """
SELECT 
    TABLE_NAME, 
    COLUMN_NAME, 
    DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
ORDER BY TABLE_NAME, ORDINAL_POSITION
"""
df = pd.read_sql(query, conn)
print(df.to_string())

