import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sqlalchemy import create_engine

# Připojení k databázi
engine = create_engine('postgresql://postgres:postgres@localhost:5432/ODM_db')

# SQL dotaz – omezíme se na 10 000 záznamů, odstraníme chybějící data
query = """
SELECT 
    e.event_type,
    p.brand,
    p.category_code,
    e.price
FROM events_fact e
JOIN product_dim p ON e.product_id = p.product_id
WHERE e.event_type IN ('view', 'cart', 'purchase') 
  AND p.brand IS NOT NULL 
  AND p.category_code IS NOT NULL 
  AND e.price IS NOT NULL
LIMIT 10000
"""
df = pd.read_sql(query, engine)

# 🎯 Cílová proměnná – 1 = purchase, 0 = jiné
df['is_purchase'] = (df['event_type'] == 'purchase').astype(int)

# Vstupní proměnné
X = df[['brand', 'category_code', 'price']]
y = df['is_purchase']

# One-hot encoding pro kategorické proměnné
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['brand', 'category_code'])
], remainder='passthrough')  # price zůstává beze změny

# Pipeline: předzpracování + klasifikační model
clf_pipeline = Pipeline([
    ('preprocessing', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced'))
])

# Rozdělení dat
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Trénování
clf_pipeline.fit(X_train, y_train)

# Vyhodnocení
y_pred = clf_pipeline.predict(X_test)

print("Classification report:\n", classification_report(y_test, y_pred))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
