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
def get_balance_sheet(ticker: str) -> pd.DataFrame:
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
    return stock.balance_sheet

@tool
def get_income_statement(ticker: str) -> pd.DataFrame:
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
    return stock.income_stmt

@tool
def get_cash_flow(ticker: str) -> pd.DataFrame:
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
    return stock.cash_flow

@tool
def calculate_graham_number(income_statement: pd.DataFrame, balance_sheet: pd.DataFrame) -> str:
    '''
    Calculates the Graham Number

    Args:
        income_statement (pd.DataFrame): The income statement of the company
        balance_sheet (pd.DataFrame): The balance sheet of the company

    Returns:
        graham_number (str): The Graham Number of the company over a few years
    '''

    # get the data from the balance sheet and income statement
    diluted_eps = income_statement.loc['Diluted EPS']
    book_value = balance_sheet.loc['Stockholders Equity']
    shares_outstanding = balance_sheet.loc['Shares Outstanding']

    # calculate book value per share
    book_value_ps = book_value / shares_outstanding

    graham_number = (22.5 * diluted_eps * book_value_ps) ** 0.5
    graham_number = graham_number.dropna()

    return graham_number.to_string()

@tool
def calculate_roe(balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> str:
    '''
    Calculates the Return on Equity, given the balance sheet and income statement.

    Args:
        balance_sheet (pd.DataFrame): The balance sheet of the company
        income_statement (pd.DataFrame): The income statement of the company

    Returns:
        roe (str): The Return On Equity (ROE) of the company over a few years
    '''
    # get the data from the balance sheet and income statement
    net_income = income_statement.loc['Net Income']
    shareholders_equity = balance_sheet.loc['Stockholders Equity']

    roe = (net_income / shareholders_equity).dropna()

    return roe.to_string()