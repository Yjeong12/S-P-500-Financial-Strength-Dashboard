import pandas as pd
import requests

#1. Import S&P 500 Companies List
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

  # Add header Information
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
  # Get page content first with "requests"
response = requests.get(url, headers=headers)

sp500 = pd.read_html(response.text)[0]
print(sp500.head())

#2. Reduce Analysis Targets > Select 120 samples
sp500_sample = sp500.sample(n=120, random_state=42)

import yfinance as yf

  # Change Ticker name from "." > "-"
sp500_sample['Symbol'] = sp500_sample['Symbol'].str.replace('.', '-', regex=False)


#3. Data collection 
import yfinance as yf
import pandas as pd

data_list = []

for symbol in sp500_sample['Symbol']:
    try:
        ticker = yf.Ticker(symbol)

        # Income Statement
        info = ticker.info
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet

        # Import latest year data
        revenue = financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else None
        net_income = financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else None
        total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else None
        total_debt = balance_sheet.loc["Total Debt"].iloc[0] if "Total Debt" in balance_sheet.index else None

        data = {
            "Ticker": symbol,
            "MarketCap": info.get("marketCap"),
            "PE": info.get("trailingPE"),
            "Revenue": revenue,
            "NetIncome": net_income,
            "TotalAssets": total_assets,
            "TotalDebt": total_debt
        }

        data_list.append(data)

    except Exception as e:
        print(f"Error with {symbol}: {e}")
        continue

df = pd.DataFrame(data_list)
print(df.head())
print(len(df))

#4. Merge
df = df.merge(
    sp500_sample[['Symbol', 'GICS Sector']],
    left_on='Ticker',
    right_on='Symbol',
    how='left'
)

df.rename(columns={"GICS Sector": "Sector"}, inplace=True)

print(df.head())

#5. Check missing values
print(df.isnull().sum())

#6. Use dropna() to clean up only the core columns, not the whole
df_clean = df.dropna(subset=[
    "MarketCap",
    "Revenue",
    "NetIncome",
    "TotalAssets",
    "TotalDebt"
]).copy()

print(df_clean.head())
print(len(df_clean))

#7. Save file to the computer
df_clean.to_csv("sp500_financial_data.csv", index=False)

#--------------------Step 1 over-------------------------

#Make a copy to protect the data
analysis_df = df_clean.copy()

#8 Calculate Ratios
analysis_df["ProfitMargin"] = analysis_df["NetIncome"] / analysis_df["Revenue"]
analysis_df["ROA"] = analysis_df["NetIncome"] / analysis_df["TotalAssets"]
analysis_df["DebtRatio"] = analysis_df["TotalDebt"] / analysis_df["TotalAssets"]
analysis_df["EarningsYield"] = 1 / analysis_df["PE"]


#9 Hard to compare because the market capitalization is too big > Use "log"
import numpy as np

analysis_df["LogMarketCap"] = np.log(analysis_df["MarketCap"])

#10 Create a size group by dividing the company into three based on market capitalization
analysis_df["SizeGroup"] = pd.qcut(
    analysis_df["MarketCap"],
    q=3,
    labels=["Smaller", "Mid", "Large"]
)

#Check Result
print(analysis_df[[
    "Ticker", "Sector", "Revenue", "NetIncome",
    "ProfitMargin", "ROA", "DebtRatio",
    "PE", "EarningsYield", "MarketCap", "LogMarketCap", "SizeGroup"
]].head())


#11 Check outliers (Important!)  
print(analysis_df[["ProfitMargin", "ROA", "DebtRatio", "EarningsYield"]].describe())


#12 Cleanup some Outliers
analysis_df = analysis_df[
    (analysis_df["ProfitMargin"] > -1) &
    (analysis_df["ProfitMargin"] < 0.8) &
    (analysis_df["ROA"] > -0.3) &
    (analysis_df["ROA"] < 0.4) &
    (analysis_df["DebtRatio"] >= 0) &
    (analysis_df["DebtRatio"] < 1.2)
].copy()

#Number of data after processing 118 -> 116
print(len(analysis_df))
print(analysis_df.describe())


#Step 4.
#13 Calculate the mean by sector
sector_summary = analysis_df.groupby("Sector")[[
    "ProfitMargin",
    "ROA",
    "DebtRatio",
    "EarningsYield"
]].mean()

print(sector_summary.sort_values(by="ProfitMargin", ascending=False))


#Check the number of companies by sector (for checking data balance)
print(analysis_df["Sector"].value_counts())


#14 Generating csv files for final analysis after outlier processing
analysis_df.to_csv("sp500_ratio_analysis.csv", index=False)

#15 Create Sector Summary file
sector_summary = analysis_df.groupby("Sector")[[
    "ProfitMargin",
    "ROA",
    "DebtRatio",
    "EarningsYield"
]].mean().reset_index()

sector_summary.to_csv("sector_summary.csv", index=False)