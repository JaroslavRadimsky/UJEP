import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pyodbc


conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\MSSQLSERVER01;"
    r"DATABASE=AdventureWorksDW2019;"
    r"Trusted_Connection=yes;"
)

query = """
SELECT 
    c.YearlyIncome,
    c.TotalChildren,
    SUM(f.SalesAmount) AS TotalSpent,
    COUNT(f.SalesOrderNumber) AS OrderCount
FROM DimCustomer c
JOIN FactInternetSales f ON c.CustomerKey = f.CustomerKey
WHERE c.TotalChildren IS NOT NULL
GROUP BY 
    c.CustomerKey, c.Gender, c.MaritalStatus, c.YearlyIncome, c.TotalChildren
"""
df = pd.read_sql(query, conn)


X_cluster = df[['YearlyIncome', 'TotalChildren', 'TotalSpent', 'OrderCount']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='TotalSpent', y='OrderCount', hue='Cluster', palette='Set2', s=100)
plt.title("KMeans shlukování podle útraty a počtu objednávek")
plt.tight_layout()
plt.savefig("kmeans_shlukovani.png")
plt.close()

print("Výstup uložený jako 'kmeans_shlukovani.png'")
