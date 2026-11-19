import pandas as pd
import matplotlib.pyplot as plt
import pyodbc
from sklearn.linear_model import LinearRegression


conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\MSSQLSERVER01;"
    r"DATABASE=AdventureWorksDW2019;"
    r"Trusted_Connection=yes;"
)



query = """
SELECT CalendarYear, SUM(Quantity) AS TotalQuantity
FROM vTimeSeries
GROUP BY CalendarYear
ORDER BY CalendarYear
"""

df = pd.read_sql(query, conn)
conn.close()


X = df[['CalendarYear']]
y = df['TotalQuantity']
model = LinearRegression()
model.fit(X, y)


future_years = pd.DataFrame({'CalendarYear': list(range(df['CalendarYear'].max() + 1, df['CalendarYear'].max() + 6))})
future_years['PredictedQuantity'] = model.predict(future_years)


plt.figure(figsize=(10, 5))
plt.plot(df['CalendarYear'], df['TotalQuantity'], marker='o', label='Historická data')
plt.plot(future_years['CalendarYear'], future_years['PredictedQuantity'], marker='x', linestyle='--', color='orange', label='Predikce')
plt.title('Predikce počtu prodaných kusů podle roku')
plt.xlabel('Rok')
plt.ylabel('Počet kusů')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('predikce_prodeje.png')
plt.show()

print("Výstup uložený jako 'predikce_prodeje.png'")
