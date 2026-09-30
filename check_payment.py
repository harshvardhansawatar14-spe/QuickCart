import os
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=os.getenv("QUICKCART_MYSQL_PASSWORD"),
    database="quickcart_ecommerce"
)

cursor = conn.cursor()

cursor.execute("""
SELECT DeliveryStatus, COUNT(*) AS Count
FROM fact_deliveries
GROUP BY DeliveryStatus
""")

for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()