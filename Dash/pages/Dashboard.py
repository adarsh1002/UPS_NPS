# UPS vs NPS Comparison Dashboard with Debugging

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
# Load Data
st.title("Government Servant Pension Comparison: UPS vs NPS")
CPC_YEARS = {
    '8CPC': 2026,
    '9CPC': 2036,
    '10CPC': 2046,
    '11CPC': 2056,
}
BASE_CPC = '7CPC'
@st.cache_data
def load_data():
    pay_matrix = pd.read_excel("7cpclong.xlsx")
    da_table = pd.read_excel("DAtable.xlsx")
    da_table['Date'] = pd.to_datetime(da_table['Date'])
    pay_matrix['Pay_Position'] = pd.to_numeric(pay_matrix['Pay_Position'], errors='coerce')
    pay_matrix['CPC'] = '7CPC'
    pay_matrix=pay_matrix.dropna(subset="Basic_Pay")
    return pay_matrix, da_table

pay_matrix, da_table = load_data()
unique_levels = sorted(pay_matrix['Level'].dropna().unique())
col1, col2,col3 = st.columns(3)
with col1:
    st.subheader("Joining Details")
    joining_date = pd.to_datetime(st.date_input("Date of Joining", value=date(2016, 12, 13)))
    retirement_age = st.slider("Retirement Age", 58, 65, 60)
    current_age = st.slider("Current Age", 20, 60, 34)
    pay_comm_increase = st.slider("Average Pay Commission Increase (%)", 10, 50, 25) / 100
with col2:
    st.subheader("Pay Details")
    initial_level = st.selectbox("Initial Pay Level", unique_levels)
    initial_position = st.number_input("Initial Pay Position", min_value=1, max_value=40, value=1)
    date_of_increment = st.selectbox("Date of Annual Increment", ["January", "July"])
    promotion_interval = st.slider("Promotion Every (Years)", 2, 10, 4)
with col3:
    st.subheader("NPS Details")
    nps_contribution_rate = st.slider("Total NPS Contribution Rate (% of Basic + DA)", 10, 30, 20) / 100
    nps_return = st.slider("NPS Annual Return Rate (%)", 5.0, 12.0, 8.0) / 100
    annuity_pct = st.slider("% of Corpus Converted to Annuity", 40, 80, 60) / 100
    annuity_rate = st.slider("Annual Annuity Rate (%)", 5.0, 8.0, 6.0) / 100
    life_expectancy_years = st.slider("Expected Years to Live Beyond Retirement", min_value=1, max_value=50, value=20)

def generate_cpc_tables(base_matrix, da_table, pay_comm_increase):
    all_cpc_tables = [base_matrix.copy()]
    cpc_years = CPC_YEARS.copy()
    prev_cpc = BASE_CPC
    for cpc, cpc_start_year in cpc_years.items():
        prev_cpc_table = all_cpc_tables[-1]
        da_july_date = pd.Timestamp(f"{cpc_start_year-1}-07-01")
        da_rate_row = da_table[da_table['Date'] <= da_july_date].sort_values('Date', ascending=False)
        if not da_rate_row.empty:
            da_rate = float(da_rate_row.iloc[0]['Rate'])
        else:
            da_rate = 0.0
        fitment = (1 + da_rate) * (1 + pay_comm_increase)
        new_table = prev_cpc_table.copy()
        new_table['Basic_Pay'] = (new_table['Basic_Pay'] * fitment).round()
        new_table['CPC'] = cpc
        all_cpc_tables.append(new_table)
    return pd.concat(all_cpc_tables, ignore_index=True)
pay_matrix_full = generate_cpc_tables(pay_matrix, da_table, pay_comm_increase)
# Functions
def create_new_cpc_matrix(old_matrix, da_table, new_cpc_base_year, pay_comm_increase, new_cpc):
    levels = old_matrix['Level'].unique()
    new_rows = []
    july_da = da_table[da_table['Date'] == pd.Timestamp(f"{new_cpc_base_year}-07-01")]['Rate'].max()
    if pd.isna(july_da):
        july_da = 0.0
    factor = (1 + july_da) * (1 + pay_comm_increase / 100)
    for level_id in levels:
        level_rows = old_matrix[old_matrix['Level'] == level_id].copy()
        level_rows = level_rows.sort_values(by='Pay_Position')
        level_rows['Basic_Pay'] = level_rows['Basic_Pay'] * factor
        level_rows['CPC'] = new_cpc
        new_rows.append(level_rows)
    return pd.concat(new_rows)


# User Inputs


# --- Simulation Timeline ---
retire_year = datetime.now().year + (retirement_age - current_age)
retire_date = datetime(retire_year, joining_date.month, joining_date.day)
months = pd.date_range(start=joining_date, end=retire_date, freq='MS')
# Service duration
service_months = (retire_date.year - joining_date.year) * 12 + (retire_date.month - joining_date.month)
completed_six_months = service_months // 6



# --- Main Calculation Loop ---
records = []
level = initial_level
position = initial_position
current_cpc = BASE_CPC
cpc_years_sorted = [(BASE_CPC, joining_date.year)] + [(cpc, y) for cpc, y in CPC_YEARS.items()]
cpc_pointer = 0
basic_pay = pay_matrix_full.query("Level == @level and Pay_Position == @position and CPC == @current_cpc")['Basic_Pay'].values[0]
nps_corpus = 0.0
current_da = 0.0

for i, month in enumerate(months):
    year = month.year
    is_jan = month.month == 1
    is_july = month.month == 7
    pay_commission_applied = ""

    # Switch CPC if month/year matches new CPC cycle
    if (cpc_pointer + 1 < len(cpc_years_sorted)) and (year == cpc_years_sorted[cpc_pointer + 1][1]) and is_jan:
        cpc_pointer += 1
        current_cpc = cpc_years_sorted[cpc_pointer][0]
        pay_commission_applied = current_cpc
        # Fetch new Basic Pay from the new CPC matrix
        basic_pay_new = pay_matrix_full.query(
         "Level == @level and Pay_Position == @position and CPC == @current_cpc"
            )['Basic_Pay']
        if not basic_pay_new.empty:
            basic_pay = basic_pay_new.values[0]
    # Reset DA after each CPC
        current_da = 0.0

    # DA increases every Jan and July at 3%
    if is_jan or is_july:
        current_da += 0.03

    da_amt = basic_pay * current_da
    total_emoluments = basic_pay + da_amt

    # Increment
    if (date_of_increment == "January" and is_jan) or (date_of_increment == "July" and is_july):
        next_position = position + 1
        new_pay = pay_matrix_full.query("Level == @level and Pay_Position == @next_position and CPC == @current_cpc")['Basic_Pay']
        if not new_pay.empty:
            basic_pay = new_pay.values[0]
            position = next_position

    # Promotion
    if ((year - joining_date.year) % promotion_interval == 0 and is_jan and year != joining_date.year):
        current_index = unique_levels.index(level)
        if current_index + 1 < len(unique_levels):
            next_level = unique_levels[current_index + 1]
            promoted_pay = pay_matrix_full.query("Level == @next_level and Pay_Position == 1 and CPC == @current_cpc")['Basic_Pay']
            if not promoted_pay.empty:
                level = next_level
                basic_pay = promoted_pay.values[0]
                position = 1

    # NPS corpus
    monthly_contribution = total_emoluments * nps_contribution_rate
    nps_corpus = (nps_corpus + monthly_contribution) * ((1 + nps_return) ** (1 / 12))

    records.append({
        "Month": month.strftime("%b-%Y"),
        "Year": year,
        "Level": level,
        "Position": position,
        "CPC": current_cpc,
        "Basic Pay": round(basic_pay),
        "DA Rate": round(current_da, 2),
        "DA Amount": round(da_amt),
        "Total Emoluments": round(total_emoluments),
        "Monthly NPS Contribution": round(monthly_contribution),
        "NPS Corpus": round(nps_corpus),
        "Pay Commission Applied": pay_commission_applied
    })

# --- Final Outputs ---
df = pd.DataFrame(records)
final_basic = basic_pay
ups_pension = 0.5 * final_basic
nps_annuity_amount = (nps_corpus * annuity_pct) * annuity_rate
# df is your progression DataFrame with all months until retirement
last_da_pct = df.iloc[-1]['DA Rate']  # e.g., 0.69 for 69%
# UPS lumpsum (gratuity) as per new rule
ups_lumpsum = final_basic * (completed_six_months / 10)
nps_lumpsum = nps_corpus * (1 - annuity_pct)
# Total payouts over life expectancy
months_retired = life_expectancy_years * 12
ups_monthly_pension = ups_pension * (1)

da_post_retire = last_da_pct  # Start from DA% at retirement!
total_ups_paid = 0.0

for i in range(months_retired):
    if i % 6 == 0 and i != 0:
        da_post_retire += 0.03
    month_pension = ups_monthly_pension * (1 + da_post_retire)
    total_ups_paid += month_pension
nps_monthly_annuity = (nps_corpus * annuity_pct * annuity_rate) / 12
total_nps_paid = nps_monthly_annuity * months_retired

# --- Results ---
st.subheader("Monthly Pay Progression Table")
st.dataframe(df)

st.subheader("Pension Comparison at Retirement")
st.markdown(f"**UPS Monthly Pension:** ₹{ups_pension:,.0f}")
st.markdown(f"**NPS Monthly Pension (Estimated):** ₹{nps_annuity_amount / 12:,.0f}")

st.subheader("Total NPS Corpus at Retirement")
st.markdown(f"**Corpus:** ₹{nps_corpus:,.0f}")

st.subheader("Lumpsum & Total Benefits")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**UPS Lumpsum :** ₹{ups_lumpsum:,.0f}")
    st.markdown(f"**Total UPS Pension (with DA escalation, {life_expectancy_years} yrs):** ₹{total_ups_paid:,.0f}")
with col2:
    st.markdown(f"**NPS Lumpsum:** ₹{nps_lumpsum:,.0f}")
    st.markdown(f"**Total NPS Annuity ({life_expectancy_years} yrs):** ₹{total_nps_paid:,.0f}")
# View each CPC matrix
#st.subheader("Current Pay Matrices by CPC")
#for cpc in sorted(pay_matrix_full['CPC'].unique()):
   # st.markdown(f"### {cpc} Pay Matrix")
   # st.dataframe(pay_matrix_full[pay_matrix_full['CPC'] == cpc].sort_values(['Level', 'Pay_Position']))
