import streamlit as st

st.title("About the UPS vs NPS Pension Dashboard")

st.markdown("""
## 1. Introduction

This dashboard is designed to simulate and compare the retirement benefits of government servants in India under two major pension regimes:

- **Unified Pension Scheme (UPS)**
- **National Pension Scheme (NPS)**

It leverages the **7th Central Pay Commission (CPC) pay matrix** as the base and dynamically generates future pay matrices for subsequent pay commissions (8CPC, 9CPC, etc.) using user-defined parameters and the DA table. The goal is to provide a transparent, scenario-based comparison to aid both policy makers and individual government employees in understanding the impact of career progression, DA growth, and pay commission reforms on pension outcomes.

---

## 2. Data Inputs

- **7th CPC Pay Matrix:**  
  A table of basic pay values for each pay level and position as per the 7th Central Pay Commission.

- **DA (Dearness Allowance) Table:**  
  A chronological table of DA rates with their effective dates.

---

## 3. Key Features and Workflow

### A. User Inputs

The dashboard offers the following user-controllable inputs:

- Date of joining
- Current age and desired retirement age
- Initial pay level and pay position
- Date of annual increment (January or July)
- Frequency of promotion (years between promotions)
- Average pay commission increase (%) (slider, e.g. 25%)
- NPS contribution rate, NPS return rate, annuity % conversion, and annuity rate

These parameters allow users to model different scenarios of career and pension growth.

---

### B. Pay Matrix Generation (CPC Simulation)

**Pay Commission Logic:**

- **CPC Timelines:**  
  The code simulates future pay commissions (e.g., 8CPC in 2026, 9CPC in 2036, and so on).

- **Fitment Factor:**  
  At each new CPC, the fitment for each basic pay entry is:

New Pay = Old Pay × (1 + DA as on last July) × (1 + Pay Commission Increase)

- DA as on last July is fetched from the DA table.
- Pay Commission Increase is set by the user slider.

- **DA Reset:**  
After each pay commission, DA is reset to zero, and subsequent DA growth resumes at the prescribed periodic increment (typically every six months).

- **Matrix Integrity:**  
The pay matrix for each CPC is regenerated so every pay level and position always has a corresponding value.

---

### C. Salary Progression Simulation

For every month of service (from joining to retirement), the dashboard simulates:

- DA accrual (usually 3% every Jan and July)
- Annual increments (moves to next pay position at selected increment month)
- Promotions (moves to next pay level at defined intervals)
- Pay commission jumps (in January of the CPC year, pay is updated as per new matrix)
- DA resets to zero after every pay commission

At each step, the simulation calculates:

- Current basic pay, DA rate, DA amount, total emoluments
- NPS contribution and corpus growth (with compounding at the selected rate)

---

### D. Pension Outputs

- **NPS Pension:**  
At retirement, a user-selected percentage of the NPS corpus is converted to an annuity, and the resulting monthly pension is displayed based on the chosen annuity rate.

- **UPS Pension:**  
The UPS pension is computed as 50% of the last drawn basic pay (or as per user’s logic).

- **Corpus and Tables:**  
The final NPS corpus, UPS monthly pension, and all monthly pay/emoluments values are shown for full transparency.

---

### E. Table and Matrix Visualization

- **Monthly Pay Progression Table:**  
Complete monthly breakdown of level, position, basic pay, DA rate, DA amount, total emoluments, NPS corpus, and pension events.

- **Pay Matrix Viewer:**  
Dynamic, user-inspectable tables for all generated pay matrices (7CPC through 11CPC) so that users can cross-check pay commission calculations for every level/position.

---

## 4. Key Assumptions

- DA grows at a fixed interval (e.g., 3% every Jan and July, but customizable).
- Promotion intervals and increment months are user-configurable.
- Pay commission increments can be set by the user for scenario analysis.
- All calculations are pre-tax and don’t account for other government-specific benefits unless added.

---

## 5. How the Code Works (Technical Workflow)

- Loads input files (pay matrix, DA table).
- Generates all future pay matrices using the correct fitment logic and DA as on July before each CPC.
- Simulates salary and pension progression for every month until retirement:
  - Applies increments/promotions/pay commissions as per logic.
  - Applies correct DA reset and accrual.
- Calculates and displays:
  - Full monthly progression table
  - All pay matrices
  - Final UPS and NPS pension figures
- Allows for interactive scenario analysis using sliders and dropdowns.

---

## 6. Validation and Debugging

- The dashboard includes real-time visibility into all generated pay matrices.
- Users can download or inspect the progression and pay matrix tables to verify the correctness of each step (e.g., that pay commission jumps and DA resets occur as per government policy).
""")

