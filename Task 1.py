import pandas as pd
import numpy as np


def calculate_volatility(file_path='NIFTY 50.xlsx', trading_days_per_year=252):
    # Read data from Excel file
    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = [c.strip() for c in df.columns.values.tolist()]

    # Calculate daily returns
    df['Daily Returns'] = (df['Close'] / df['Close'].shift(1)) - 1

    # Calculate daily volatility
    daily_volatility = df['Daily Returns'].std()

    # Calculate annualized volatility
    annualized_volatility = daily_volatility * np.sqrt(trading_days_per_year)

    return df, daily_volatility, annualized_volatility


def display_results(df, daily_volatility, annualized_volatility):
    print("Daily Volatility:", daily_volatility)
    print("Annualized Volatility:", annualized_volatility)
    print(df)


def main():
    df, daily_volatility, annualized_volatility = calculate_volatility()
    display_results(df, daily_volatility, annualized_volatility)


if __name__ == "__main__":
    main()
