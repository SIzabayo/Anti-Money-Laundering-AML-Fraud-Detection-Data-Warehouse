import csv
from faker import Faker
import random
import datetime

fake = Faker()
N_DIMS = 10000  # Number of rows for each dimension table
N_FACTS = 1000000  # Number of transaction_fact rows

def write_date_dim():
	with open("date_dim.csv", "w", newline='') as f:
		writer = csv.writer(f)
		start_date = datetime.date(2025, 1, 1)
		end_date = datetime.date(2026, 12, 31)
		for i in range(1, N_DIMS+1):
			date = fake.date_between(start_date=start_date, end_date=end_date)
			week = date.isocalendar()[1]
			month, quarter, year = date.month, (date.month - 1) // 3 + 1, date.year
			writer.writerow([i, date, week, month, quarter, year])

def write_customer_dim():
	with open("customer_dim.csv", "w", newline='') as f:
		writer = csv.writer(f)
		for i in range(1, N_DIMS+1):
			writer.writerow([
				i,
				fake.name(),
				fake.date_of_birth(minimum_age=18, maximum_age=85),
				fake.address().replace('\n', ', '),
				fake.job(),
				random.choice(['Low', 'Medium', 'High']),
				random.choice(['Complete', 'Incomplete']),
			])

def write_account_dim():
	with open("account_dim.csv", "w", newline='') as f:
		writer = csv.writer(f)
		types = ['Savings', 'Checking', 'Investment', 'Credit Card', 'Loan', 'Overdraft']
		status = ["Active", "Inactive", "Closed"]
		for i in range(1, N_DIMS+1):
			od = fake.date_between(start_date="-10y", end_date="today")
			cd = od if random.random() > 0.7 else ''
			if cd:
				cd = fake.date_between(start_date=od, end_date="today")
			writer.writerow([
				i,
				random.choice(types),
				random.choice(status),
				od,
				cd or '',
				round(random.uniform(0, 50000), 2),
			])

def write_product_dim():
	with open("product_dim.csv", "w", newline='') as f:
		writer = csv.writer(f)
		types = [
			('Credit Card', 'Standard CC'),
			('Loan', 'Personal Loan'),
			('Savings Account', 'Basic Savings Account'),
			('Checking Account', 'Standard Checking'),
			('Investment', 'Mutual Fund'),
			('Business Loan', 'Loan for SME'),
			('Overdraft', 'Account Overdraft'),
			('Mortgage', 'Home Loan')
		]
		for i in range(1, N_DIMS+1):
			typ, desc = random.choice(types)
			writer.writerow([i, typ, desc])

def write_channel_dim():
	with open("channel_dim.csv", "w", newline='') as f:
		writer = csv.writer(f)
		types = ["Online", "Branch", "ATM", "Mobile App", "POS Terminal", "Phone Banking"]
		for i in range(1, N_DIMS+1):
			writer.writerow([i, random.choice(types)])

def write_transaction_fact():
	with open("transaction_fact.csv", "w", newline='') as f:
		writer = csv.writer(f)
		txn_types = [
			"Deposit", "Withdrawal", "Wire Transfer", "Loan Payment",
			"POS Payment", "Investment Purchase", "Mortgage Payment"
		]
		countries = ["South Africa", "Nigeria", "USA", "UK", "Germany"]
		for _ in range(N_FACTS):
			writer.writerow([
				random.randint(1, N_DIMS),
				random.randint(1, N_DIMS),
				random.randint(1, N_DIMS),
				random.randint(1, N_DIMS),
				random.randint(1, N_DIMS),
				round(random.uniform(10, 50000), 2),
				random.choice(txn_types),
				random.choice(countries),
				random.choice(countries),
			])

if __name__ == "__main__":
	write_date_dim()
	write_customer_dim()
	write_account_dim()
	write_product_dim()
	write_channel_dim()
	write_transaction_fact()
	print("CSV files generated.")