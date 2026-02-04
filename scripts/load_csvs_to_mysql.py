import pandas as pd
from sqlalchemy import create_engine

# MySQL connection details
user = 'root'  # Update if needed
password = ''  # Update if you have a password
host = 'localhost'
port = 3306
database = 'aml_fraud_dw'

# CSV files and their corresponding table names
csv_table_map = {
    'date_dim.csv': 'date_dim',
    'customer_dim.csv': 'customer_dim',
    'account_dim.csv': 'account_dim',
    'product_dim.csv': 'product_dim',
    'channel_dim.csv': 'channel_dim',
    'transaction_fact.csv': 'transaction_fact',
}

# Create SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

for csv_file, table_name in csv_table_map.items():
    print(f'Loading {csv_file} into {table_name}...')
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f'Loaded {csv_file} into {table_name}.')

print('All CSV files loaded into MySQL database.')
