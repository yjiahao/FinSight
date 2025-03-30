from langchain_core.tools import tool

import yfinance as yf

import pandas as pd
import numpy as np

# TODO: add more tools for the LLM using the yfinance API: look at balance sheet, income statement, cash flow, etc.
# TODO: what happens if we need data from different dataframes? E.g. balance sheet, income statement for calculating ROE
# at the moment, just letting agent decide how to use the tools and letting it chain them together

# TODO: change the tool inputs to be taking in serializable objects instead of pandas dataframes

# tools for the LLM agent to use

# functions to access financial statements
# NOTE: need to see if we can work with just giving the entire balance sheet, or extract components of it to reduce token size
@tool
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

@tool
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

@tool
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

@tool
def calculate_graham_number(income_statement: dict, balance_sheet: dict) -> dict:
    '''
    Calculates the Graham Number

    Args:
        income_statement (dict): The income statement of the company
        balance_sheet (dict): The balance sheet of the company

    Returns:
        graham_number (dict): The Graham Number of the company over a few years, with date as key and Graham Number as value
    '''

    diluted_eps = income_statement['Diluted EPS']
    book_value = balance_sheet['Stockholders Equity']
    shares_outstanding = balance_sheet['Ordinary Shares Number']

    # convert into format we can use
    graham_numbers = {}

    for date, eps, book_value, shares_outstanding in zip(diluted_eps.keys(), diluted_eps.values(), book_value.values(), shares_outstanding.values()):
        if np.isnan(eps) or np.isnan(book_value) or np.isnan(shares_outstanding):
            continue
        graham_numbers[date] = {}
        book_value_ps = book_value / shares_outstanding
        graham_numbers[date] = (22.5 * eps * book_value_ps) ** 0.5

    return graham_numbers

@tool
def calculate_roe(balance_sheet: dict, income_statement: dict) -> dict:
    '''
    Calculates the Return on Equity, given the balance sheet and income statement.

    Args:
        balance_sheet (dict): The balance sheet of the company
        income_statement (dict): The income statement of the company

    Returns:
        roe (dict): The Return On Equity (ROE) of the company over a few years, with key as date and value as ROE
    '''
    net_income = income_statement['Net Income']
    shareholders = balance_sheet['Stockholders Equity']

    roe = {}
    for date, net_income, shareholders in zip(net_income.keys(), net_income.values(), shareholders.values()):
        if np.isnan(net_income) or np.isnan(shareholders):
            continue
        roe[date] = {}
        roe[date] = net_income / shareholders
    
    return roe

@tool
def get_pe_ratio(ticker: str) -> float:
    '''
    Calculates the Price to Earnings (P/E) ratio, given the income statement.
    Market value per share / EPS

    Args:
        income_statement (dict): The income statement of the company

    Returns:
        pe_ratio (dict): The P/E ratio of the company over a few years, with key as date and value as P/E ratio
    '''
    data = yf.Ticker(ticker)
    pe_ratio = data.info['trailingPE']

    return pe_ratio

@tool
def get_earnings_yield(ticker: str) -> float:
    '''
    Calculates the Earnings Yield, given the income statement.
    Earnings Yield = EPS / Market Value per Share

    Args:
        income_statement (dict): The income statement of the company

    Returns:
        earnings_yield (dict): The Earnings Yield of the company over a few years, with key as date and value as Earnings Yield
    '''
    data = yf.Ticker(ticker)
    pe_ratio = data.info['trailingPE']

    return 1 / pe_ratio