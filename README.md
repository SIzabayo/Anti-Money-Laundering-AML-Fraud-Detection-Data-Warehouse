# Anti-Money-Laundering-AML-Fraud-Detection-Data-Warehouse
AML &amp; Fraud Data Warehouse: A scalable MySQL data warehouse solution for Anti-Money Laundering and Fraud Detection analytics, featuring synthetic data generation, ETL scripts, and an interactive Streamlit dashboard for advanced financial risk monitoring.

## Features

- **Star Schema Design:** Transaction fact table and rich dimensions for flexible analytics
- **Synthetic Data Generator:** Python + Faker to simulate real-world financial transactions
- **Efficient Bulk Loading:** Fast CSV import using MySQL `LOAD DATA LOCAL INFILE`
- **Interactive Dashboard:**  
  - KPIs: Total transactions, high-value cases, suspicious flags  
  - Monthly trends, channel and risk analysis  
  - Top customers, foreign transactions and OLAP-style explorer
- **Visualization:** Altair-powered charts in Streamlit web app

## Architecture

- **Database:** MySQL (or MariaDB)
- **ETL/Data Generation:** Python (Faker, pandas)
- **Dashboard:** Streamlit + Altair

## Quickstart

1. **Install requirements:**
   ```bash
   pip install streamlit pandas altair sqlalchemy pymysql faker
   ```

2. **Set up database:**
   - Create the database and tables with provided SQL scripts.
   - Generate synthetic data with Python scripts.
   - Load CSVs into MySQL using `LOAD DATA LOCAL INFILE`.

3. **Run Dashboard:**
   ```bash
   streamlit run main.py
   ```
   or
   ```bash
   python -m streamlit run main.py
   ```

4. **View at:**  
   [http://localhost:8501](http://localhost:8501) in your browser.

## Screenshots
<img width="975" height="355" alt="image" src="https://github.com/user-attachments/assets/c89edb13-86f8-4de5-b461-7a630afa68f5" />
<img width="1919" height="661" alt="image" src="https://github.com/user-attachments/assets/c9870d77-f2f6-4ba4-8d25-dc434b9569e2" />
<img width="1858" height="562" alt="image" src="https://github.com/user-attachments/assets/c558d72f-c402-4c1b-9237-16e123345789" />
<img width="975" height="317" alt="image" src="https://github.com/user-attachments/assets/13e44127-510e-4567-8a8e-7bce28af3811" />
<img width="975" height="416" alt="image" src="https://github.com/user-attachments/assets/3629d96d-da36-48ac-af93-21c9d8a69e1b" />
<img width="1845" height="909" alt="image" src="https://github.com/user-attachments/assets/8cdce78b-6610-430b-9d7a-4911b3fb5b01" />




## Project Structure

```
├── data/
├── scripts/
│   ├── generate_data.py
│   └── load_data.sql
├── main.py
├── README.md
└── ... (add files as needed)
```

## License

MIT License

## Credits

Developed by Samuel Izabayo, for educational and financial analytics demonstration purposes.
buymeacoffee.com/samtechgrp
