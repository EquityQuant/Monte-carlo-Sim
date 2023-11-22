import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import datetime

# Set the default Seaborn style for plots
sns.set(style='darkgrid')

def get_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        return data['Adj Close']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def calculate_monte_carlo_paths(stock_data, days_forecast=252, simulations=1000):
    returns = stock_data.pct_change()
    last_price = stock_data.iloc[-1]
    simulation_df = pd.DataFrame()

    for x in range(simulations):
        count = 0
        daily_vol = returns.std()
        price_series = [last_price]
        
        for y in range(days_forecast):
            if count == days_forecast - 1:
                break
            price = price_series[count] * (1 + np.random.normal(0, daily_vol))
            price_series.append(price)
            count += 1
        
        simulation_df[x] = price_series

    return simulation_df

def trade_simulation(simulation_df, position, num_shares):
    initial_price = simulation_df.iloc[0,0]
    final_prices = simulation_df.iloc[-1]
    if position == 'long':
        pnl = (final_prices - initial_price) * num_shares
    elif position == 'short':
        pnl = (initial_price - final_prices) * num_shares
    return pnl

def visualize_trade_results(pnl1, pnl2, ticker1, ticker2):
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    
    sns.histplot(pnl1, bins=50, kde=True, ax=axs[0], color='blue')
    axs[0].set_title(f"Distribution of P&L for {ticker1}")
    axs[0].set_xlabel("Profit & Loss")
    axs[0].set_ylabel("Frequency")
    
    sns.histplot(pnl2, bins=50, kde=True, ax=axs[1], color='orange')
    axs[1].set_title(f"Distribution of P&L for {ticker2}")
    axs[1].set_xlabel("Profit & Loss")
    axs[1].set_ylabel("Frequency")
    
    plt.tight_layout()
    plt.show()

def run_monte_carlo():
    ticker1 = input("Enter first ticker symbol (e.g., AAPL): ").upper()
    ticker2 = input("Enter second ticker symbol (e.g., MSFT): ").upper()
    start_date = input("Enter start date (YYYY-MM-DD) or leave blank for 1 year ago: ")
    end_date = input("Enter end date (YYYY-MM-DD) or leave blank for today: ")
    position1 = input(f"Choose position for {ticker1} (long/short): ").lower()
    position2 = input(f"Choose position for {ticker2} (long/short): ").lower()
    num_shares1 = int(input(f"Enter the number of shares or contracts for {ticker1}: "))
    num_shares2 = int(input(f"Enter the number of shares or contracts for {ticker2}: "))

    if not start_date:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    data1 = get_stock_data(ticker1, start_date, end_date)
    data2 = get_stock_data(ticker2, start_date, end_date)

    if data1 is not None and data2 is not None:
        simulation_df1 = calculate_monte_carlo_paths(data1)
        simulation_df2 = calculate_monte_carlo_paths(data2)

        pnl1 = trade_simulation(simulation_df1, position1, num_shares1)
        pnl2 = trade_simulation(simulation_df2, position2, num_shares2)

        visualize_trade_results(pnl1, pnl2, ticker1, ticker2)

        if input("Would you like to download the simulation and P&L results as a PDF? (yes/no): ").lower() == 'yes':
            filename = 'monte_carlo_trade_simulations.pdf'
            with PdfPages(filename) as pdf:
                sns.histplot(pnl1, bins=50, kde=True, color='blue')
                plt.title(f"Distribution of P&L for {ticker1}")
                plt.xlabel("Profit & Loss")
                plt.ylabel("Frequency")
                pdf.savefig()
                plt.close()

                sns.histplot(pnl2, bins=50, kde=True, color='orange')
                plt.title(f"Distribution of P&L for {ticker2}")
                plt.xlabel("Profit & Loss")
                plt.ylabel("Frequency")
                pdf.savefig()
                plt.close()

            print(f"Saved the simulations to {filename}")

run_monte_carlo()
