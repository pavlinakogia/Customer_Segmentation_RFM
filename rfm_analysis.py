import pandas as pd
import sqlite3

# 1. Φόρτωση δεδομένων
df = pd.read_csv('dataset/sales_data_sample.csv', encoding='unicode_escape')

# 2. Μετατροπή της ημερομηνίας σε σωστό Date Format
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])

# 3. Σύνδεση με την προσωρινή SQL βάση
conn = sqlite3.connect(':memory:')
df.to_sql('SALES_DATA', conn, index=False, if_exists='replace')

def run_query(query):
    return pd.read_sql_query(query, conn)

rfm_query = """
WITH rfm_base AS (
    SELECT 
        CUSTOMERNAME,
        CAST(julianday('2005-06-01') - julianday(MAX(ORDERDATE)) AS INT) as Recency,
        COUNT(DISTINCT ORDERNUMBER) as Frequency,
        SUM(SALES) as MonetaryValue
    FROM SALES_DATA
    GROUP BY CUSTOMERNAME
),
rfm_scores AS (
    SELECT *,
        -- Χωρίζουμε σε 5 γκρουπ. Στο Recency, το μικρότερο νούμερο παίρνει 5.
        NTILE(5) OVER (ORDER BY Recency DESC) as R_Score,
        -- Στο Frequency και Monetary, το μεγαλύτερο νούμερο παίρνει 5.
        NTILE(5) OVER (ORDER BY Frequency ASC) as F_Score,
        NTILE(5) OVER (ORDER BY MonetaryValue ASC) as M_Score
    FROM rfm_base
)
SELECT 
    CUSTOMERNAME, 
    R_Score, F_Score, M_Score,
    (R_Score + F_Score + M_Score) as Total_RFM_Score
FROM rfm_scores
ORDER BY Total_RFM_Score DESC
"""

rfm_result = run_query(rfm_query)
print(rfm_result.head(10))

rfm_result = run_query(rfm_query)
print(rfm_result.head(10)) # Δείξε τους 10 πιο "πρόσφατους" πελάτες

rfm_result.to_csv('rfm_segments.csv', index=False)
print("Το αρχείο rfm_segments.csv δημιουργήθηκε!")
