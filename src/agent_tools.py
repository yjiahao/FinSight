from langchain_core.tools import tool

import yfinance as yf

import pandas as pd
import numpy as np

# TODO: add more tools for the LLM using the yfinance API: look at balance sheet, income statement, cash flow, etc.
# TODO: what happens if we need data from different dataframes? E.g. balance sheet, income statement for calculating ROE
# at the moment, just letting agent decide how to use the tools and letting it chain them together

# TODO: Need some way to get the intent of the user from the query, then use the tools accordingly

# tools for the LLM agent to use

# functions to access financial statements
# NOTE: need to see if we can work with just giving the entire balance sheet, or extract components of it to reduce token size
def get_balance_sheet(ticker: str) -> dict:
    '''
    Get the balance sheet of the company given a ticker symbol.
    
    Potentially useful fields include:
        - Stockholders Equity
        - Retained Earnings
        - Total Assets
        - Net PPE
        - Gross PPE
        - Common Stock Equity
        - Total Debt
        - Tangible Book Value
        - Invested Capital
        - Cash And Cash Equivalents
        - Total Debt
        - Common Stock Equity
        - Current Assets
        - Current Liabilities
        - Receivables
        - Total Liabilities Net Minority Interest
        - Capital Lease Obligations
        - Working Capital
        - Accounts Receivable
        - Inventory
        - Cash Cash Equivalents And Short Term Investments
        - Other Short Term Investments

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        dict: The balance sheet of the company
    '''
    
    stock = yf.Ticker(ticker)
    bs = stock.balance_sheet.transpose()
    bs.index = bs.index.strftime('%Y-%m-%d')

    return bs.to_dict()

def get_income_statement(ticker: str) -> dict:
    '''
    Get the income statement of the company given a ticker symbol.

    Potentially useful fields include:
        - Revenue
        - Cost Of Goods Sold
        - Gross Profit
        - Operating Income
        - Net Income
        - Earnings Before Interest And Taxes (EBIT)
        - Earnings Before Interest Taxes Depreciation And Amortization (EBITDA)
        - Earnings Before Interest And Taxes (EBIT)
        - Earnings Before Interest Taxes Depreciation And Amortization (EBITDA)

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        dict: The income statement of the company
    '''
    
    stock = yf.Ticker(ticker)
    income_statement = stock.income_stmt.transpose()
    income_statement.index = income_statement.index.strftime('%Y-%m-%d')

    return income_statement.to_dict()

def get_cash_flow(ticker: str) -> dict:
    '''
    Get the cash flow statement of the company given a ticker symbol.

    Potentially useful fields include:
        - Operating Cash Flow
        - Investing Cash Flow
        - Financing Cash Flow
        - Free Cash Flow

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        dict: The cash flow statement of the company
    '''
    stock = yf.Ticker(ticker)
    cash_flow = stock.cash_flow.transpose()
    cash_flow.index = cash_flow.index.strftime('%Y-%m-%d')

    return cash_flow.to_dict()

def calculate_graham_number(ticker: str) -> dict:
    '''
    Calculates the Graham Number. It is a measure of a stock's intrinsic value, based on the company's earnings per share (EPS) and book value per share (BVPS).
    But it does not return astock price, it returns the Graham Number.

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        graham_number (dict): The Graham Number of the company over a few years, with date as key and Graham Number as value
    '''

    # get balance sheet and income statements
    income_statement = get_income_statement(ticker)
    balance_sheet = get_balance_sheet(ticker)

    diluted_eps = income_statement['Diluted EPS']
    book_value = balance_sheet['Stockholders Equity']
    shares_outstanding = balance_sheet['Ordinary Shares Number']

    # convert into format we can use
    graham_numbers = {}

    for date, eps, book_value, shares_outstanding in zip(diluted_eps.keys(), diluted_eps.values(), book_value.values(), shares_outstanding.values()):
        if np.isnan(eps) or np.isnan(book_value) or np.isnan(shares_outstanding):
            continue
        book_value_ps = book_value / shares_outstanding
        graham_numbers[date] = round((22.5 * eps * book_value_ps) ** 0.5, 2)

    return graham_numbers

def calculate_roe(ticker: str) -> dict:
    '''
    Calculates the latest Return on Equity, given the balance sheet and income statement.

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        roe (dict): The Return On Equity (ROE) of the company over a few years, with key as date and value as ROE
    '''
    income_statement = get_income_statement(ticker)
    balance_sheet = get_balance_sheet(ticker)

    net_income = income_statement['Net Income']
    shareholders = balance_sheet['Stockholders Equity']

    roe = {}
    for date, net_income, shareholders in zip(net_income.keys(), net_income.values(), shareholders.values()):
        if np.isnan(net_income) or np.isnan(shareholders):
            continue
        roe[date] = round(net_income / shareholders, 2)
    
    return roe

def calculate_roa(ticker: str) -> dict:
    '''
    Calculates the Return on Assets, given the balance sheet and income statement.

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        roa (dict): The Return On Assets (ROA) of the company over a few years, with key as date and value as ROA
    '''
    income_statement = get_income_statement(ticker)
    balance_sheet = get_balance_sheet(ticker)

    net_income = income_statement['Net Income']
    total_assets = balance_sheet['Total Assets']

    roa = {}
    for date, net_income, total_assets in zip(net_income.keys(), net_income.values(), total_assets.values()):
        if np.isnan(net_income) or np.isnan(total_assets):
            continue
        roa[date] = round(net_income / total_assets, 2)
    
    return roa

def get_pe_ratio(ticker: str) -> dict:
    '''
    Get the P/E ratio of the company given a ticker symbol.

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        list: A list P/E ratios for each year
    '''
    
    income_statement = get_income_statement(ticker)
    eps = income_statement['Diluted EPS']

    stock = yf.Ticker(ticker)
    prices = stock.history(period='max')
    prices['year'] = prices.index.year
    year_last_prices = prices.groupby('year').last()['Close']

    pe_ratios = {}
    for date, eps in eps.items():
        if np.isnan(eps):
            continue
        year = pd.to_datetime(date).year
        if year in year_last_prices.index:
            pe_ratio = year_last_prices[year] / eps
            pe_ratios[date] = round(pe_ratio, 2)

    return pe_ratios

def get_earnings_yield(ticker: str) -> float:
    '''
    Calculates the Earnings Yield, given the income statement.
    Earnings Yield = EPS / Market Value per Share

    Args:
        income_statement (dict): The income statement of the company

    Returns:
        earnings_yield (dict): The Earnings Yield of the company over a few years, with key as date and value as Earnings Yield
    '''
    pe_ratios = get_pe_ratio(ticker)
    earnings_yield = {date: round(1 / pe_ratio, 2) for date, pe_ratio in pe_ratios.items()}
    return earnings_yield

def get_debt_to_equity_ratio(ticker: str) -> dict:
    '''
    Calculates the Debt to Equity ratio, given the stock ticker of the company.

    Args:
        ticker (str): The stock ticker of the company

    Returns:
        debt_to_equity_ratio (dict): The Debt to Equity ratio of the company over a few years
    '''
    balance_sheet = get_balance_sheet(ticker)
    equity = balance_sheet['Common Stock Equity']
    total_debt = balance_sheet['Total Debt']

    debt_to_equity_ratio = {}
    for date, equity, total_debt in zip(equity.keys(), equity.values(), total_debt.values()):
        if np.isnan(equity) or np.isnan(total_debt):
            continue
        debt_to_equity_ratio[date] = round(total_debt / equity, 2)

    return debt_to_equity_ratio

def get_gross_profit_margin(ticker: str) -> list[tuple[str, float]]:
    '''
    Calculates the Gross Profit Margin, given the stock ticker of the company.

    Args:
        ticker (str): The stock ticker of the company

    Returns:
        gross_profit_margin (list): The Gross Profit Margin of the company over a few years.
    '''
    income_statement = get_income_statement(ticker)
    total_revenue = income_statement['Total Revenue']
    gross_profit = income_statement['Gross Profit']

    gross_profit_margin = {}
    for date, total_revenue, gross_profit in zip(total_revenue.keys(), total_revenue.values(), gross_profit.values()):
        if np.isnan(total_revenue) or np.isnan(gross_profit):
            continue
        gross_profit_margin[date] = round(gross_profit / total_revenue, 2)

    return gross_profit_margin

def get_operating_margin(ticker: str) -> dict:
    '''
    Calculates the Operating Margin, given the stock ticker of the company.

    Args:
        ticker (str): The stock ticker of the company
        
    Returns:
        operating_margin (float): The Operating Margin of the company over a few years.
    '''
    income_statement = get_income_statement(ticker)
    ebit = income_statement['EBIT']
    total_revenue = income_statement['Total Revenue']

    operating_margin = {}
    for date, ebit, total_revenue in zip(ebit.keys(), ebit.values(), total_revenue.values()):
        if np.isnan(ebit) or np.isnan(total_revenue):
            continue
        operating_margin[date] = round(ebit / total_revenue, 2)

    return operating_margin

def get_net_profit_margin(ticker: str) -> dict:
    '''
    Calculates the net profit margin, given the stock ticker of the company.

    Args:
        ticker (str): The stock ticker of the company

    Returns:
        net_profit_margin (float): The net profit margin of the company
    '''
    income_statement = get_income_statement(ticker)
    net_income = income_statement['Net Income']
    total_revenue = income_statement['Total Revenue']

    net_profit_margin = {}
    for date, net_income, total_revenue in zip(net_income.keys(), net_income.values(), total_revenue.values()):
        if np.isnan(net_income) or np.isnan(total_revenue):
            continue
        net_profit_margin[date] = round(net_income / total_revenue, 2)

    return net_profit_margin

def get_current_ratio(ticker: str) -> dict:
    '''
    Calculates the current ratio, given the stock ticker of the company.

    Args:
        ticker (str): The stock ticker of the company

    Returns:
        current_ratio (float): The current ratio of the company over a few years.
    '''
    balance_sheet = get_balance_sheet(ticker)
    current_assets = balance_sheet['Current Assets']
    current_liabilities = balance_sheet['Current Debt']

    current_ratio = {}
    for date, current_assets, current_liabilities in zip(current_assets.keys(), current_assets.values(), current_liabilities.values()):
        if np.isnan(current_assets) or np.isnan(current_liabilities):
            continue
        current_ratio[date] = round(current_assets / current_liabilities, 2)

    return current_ratio

def get_working_capital(ticker: str) -> dict:
    '''
    Calculates the working capital, given the stock ticker of the company.

    Args:
        ticker (str): The stock ticker of the company

    Returns:
        working_capital (float): The working capital of the company over a few years.
    '''
    balance_sheet = get_balance_sheet(ticker)
    current_assets = balance_sheet['Current Assets']
    current_liabilities = balance_sheet['Current Debt']

    working_capital = {}
    for date, current_assets, current_liabilities in zip(current_assets.keys(), current_assets.values(), current_liabilities.values()):
        if np.isnan(current_assets) or np.isnan(current_liabilities):
            continue
        working_capital[date] = round(current_assets - current_liabilities, 2)

    return working_capital

def get_current_price(ticker: str):
    '''
    Get the current price of the stock.

    Args:
        ticker (str): The stock ticker of the company

    Returns:
        current_price (float): The current price of the stock
    '''
    data = yf.Ticker(ticker)
    current_price = data.history(period='1d')['Close'][0]

    return round(current_price, 2)

def discounted_cash_flow(ticker: str, discount_rate: float = 0.1) -> dict:
    '''
    Calculates the discounted cash flow of the company given a ticker symbol.

    Args:
        ticker (str): The ticker symbol of the company
        discount_rate (float): The discount rate to use for the DCF calculation

    Returns:
        dcf (float): The discounted cash flow of the company to arrive at a price per share
    '''
    
    cash_flow_statement = get_cash_flow(ticker)
    free_cash_flow = cash_flow_statement['Free Cash Flow']
    # to play safe, assume cash flow is constant, and we take the average of the last 5 years
    mean_free_cash_flow = np.nanmean(list(free_cash_flow.values()))
    pv_future_cash_flows = []
    for i in range(1, 6):
        discounted_cash_flow = mean_free_cash_flow / ((1 + discount_rate) ** i)
        pv_future_cash_flows.append(discounted_cash_flow)

    # calculate terminal value
    terminal_value = mean_free_cash_flow * (1 + 0.02) / (discount_rate - 0.02)
    
    total_cash_flow = sum(pv_future_cash_flows) + terminal_value

    ticker = yf.Ticker(ticker)
    shares_outstanding = ticker.info.get('sharesOutstanding')

    dcf_price = round(total_cash_flow / shares_outstanding, 2)

    return dcf_price

@tool
def get_financial_information(ticker: str) -> dict:
    '''
    Get the financial information of the company given a ticker symbol.
    Financial information includes:
        - Graham Number
        - Discounted Cash Flow (DCF), at 10% discount rate
        - Return on Equity (ROE)
        - Return on Assets (ROA)
        - P/E Ratio
        - Earnings Yield
        - Debt to Equity Ratio
        - Gross Profit Margin
        - Operating Margin
        - Net Profit Margin
        - Current Ratio
        - Working Capital
        - Current Price

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        dict: The financial information of the company with keys as the financial metric, and values as a dictionary of key as date adn value as the financial metric
    '''
    
    res = {}
    # calculate the date here
    res['graham_number'] = calculate_graham_number(ticker)
    res['discounted_cash_flow'] = discounted_cash_flow(ticker)
    res['roe'] = calculate_roe(ticker)
    res['roa'] = calculate_roa(ticker)
    res['pe_ratio'] = get_pe_ratio(ticker)
    res['earnings_yield'] = get_earnings_yield(ticker)
    res['debt_to_equity_ratio'] = get_debt_to_equity_ratio(ticker)
    res['gross_profit_margin'] = get_gross_profit_margin(ticker)
    res['operating_margin'] = get_operating_margin(ticker)
    res['net_profit_margin'] = get_net_profit_margin(ticker)
    res['current_ratio'] = get_current_ratio(ticker)
    res['working_capital'] = get_working_capital(ticker)
    res['current_price'] = get_current_price(ticker)

    return res