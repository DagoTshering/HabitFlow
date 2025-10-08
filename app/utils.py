from datetime import date, timedelta

def today():
    return date.today()

def last_n_days(n):
    base = date.today()
    return [base - timedelta(days=i) for i in range(n)]
