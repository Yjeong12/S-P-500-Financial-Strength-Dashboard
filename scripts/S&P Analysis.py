#Analysis
import pandas as pd
import numpy as np

# 1. Import data to create Sector Summary and Composite Score
analysis_df = pd.read_csv("sp500_ratio_analysis.csv")

print(analysis_df.head())
print(analysis_df.columns)
print(len(analysis_df))

#2. Create Sector summary table
sector_summary = analysis_df.groupby("Sector").agg({
    "ProfitMargin": "mean",
    "ROA": "mean",
    "DebtRatio": "mean",
    "EarningsYield": "mean",
    "MarketCap": "mean",
    "Ticker": "count"
}).reset_index()

sector_summary.rename(columns={"Ticker": "CompanyCount"}, inplace=True)

print(sector_summary.sort_values(by="ProfitMargin", ascending=False))

#3. Create Composite Score 
score_df = analysis_df.copy()

score_df["PM_z"] = (score_df["ProfitMargin"] - score_df["ProfitMargin"].mean()) / score_df["ProfitMargin"].std()
score_df["ROA_z"] = (score_df["ROA"] - score_df["ROA"].mean()) / score_df["ROA"].std()
score_df["Debt_z"] = (score_df["DebtRatio"] - score_df["DebtRatio"].mean()) / score_df["DebtRatio"].std()

score_df["FinancialStrengthScore"] = (
    score_df["PM_z"] +
    score_df["ROA_z"] -
    score_df["Debt_z"]
)

print(score_df[[
    "Ticker", "Sector", "ProfitMargin", "ROA", "DebtRatio", "FinancialStrengthScore"
]].head())

# Ex) Check Top15 companies for testing 
top_score = score_df[[
    "Ticker", "Sector", "ProfitMargin", "ROA", "DebtRatio", "FinancialStrengthScore"
]].sort_values(by="FinancialStrengthScore", ascending=False).head(15)

print(top_score)

#Save Files
sector_summary.to_csv("sector_summary.csv", index=False)
score_df.to_csv("sp500_Compositescore.csv", index=False)
top_score.to_csv("top_financial_strength.csv", index=False)