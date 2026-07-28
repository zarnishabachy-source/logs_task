import pandas as pd
import re

df = pd.read_csv(r'C:\Users\User\OneDrive\Desktop\logs\cleaned_files\server-logs-table-Error_Exception.csv',
                 usecols=['SQL / Message Content', 'Client IP'])

# Extract subdomain from SQL queries like: [["subdomain", "alimran6512"], ...]
pattern = r'\["subdomain",\s*"([^"]+)"\]'
df['Company'] = df['SQL / Message Content'].astype(str).str.extract(pattern)

print('Rows with company extracted:', df['Company'].notna().sum())
print('Unique companies found:', df['Company'].nunique())
print('\nSample companies:')
print(df['Company'].dropna().unique())

# Check how IP maps to company
sample = df[df['Company'].notna()][['Client IP','Company']].drop_duplicates().head(10)
print('\nIP -> Company sample:')
print(sample.to_string())
