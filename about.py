import streamlit as st

st.title("About the UPS vs NPS Pension Dashboard")

st.markdown("""
# Dashboard Overview

This dashboard simulates and compares the retirement benefits of government servants under the Unified Pension Scheme (UPS) and National Pension Scheme (NPS).

## Key Features

- Dynamic pay progression simulation using the 7th CPC pay matrix and DA rates.
- Automated pay commission matrix generation for future CPCs with user-defined fitment factors.
- Scenario analysis of promotions, increments, DA accrual, and NPS returns.
- Side-by-side comparison of pension benefits under UPS and NPS.

## How It Works

- The dashboard uses your inputs (joining date, level, etc.) to simulate your pay career.
- Each new pay commission applies a fitment factor calculated using DA as of July prior to the CPC, and the percentage increment you select.
- DA resets after each pay commission.
- NPS corpus growth and pension annuity are calculated using the rates you choose.

## Data Sources

- Pay Matrix: 7th CPC government tables
- DA Table: Government DA notifications

## Who Can Use This

- Policy makers, government employees, auditors, or anyone interested in pension simulation!

**Try the Dashboard page to start your simulation.**
""")
