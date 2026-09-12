# Airline Hedging & Econometrics ETL Pipeline (2020–2024)

Automated data extraction (ETL) and panel econometrics pipeline analyzing the financial impact of jet fuel price volatility and corporate hedging strategies on European airline operating margins (Ryanair Holdings plc vs. Deutsche Lufthansa AG).

---

## 1. Executive Summary & Key Results

* **Empirical Proof of Hedging Efficacy:** The interaction term between fuel market price and hedging coverage ($\ln(\text{JetFuel}) \times \text{Hedge}$) is positive and statistically significant ($\beta = +0.6328, p = 0.034$). This confirms that active corporate hedging strategies effectively decoupled operational cash flows from spot kerosene price surges during the 2022 European energy crisis.


* **Econometric Diagnostics:** White's heteroskedasticity-consistent covariance matrix (HC1) was applied following rejection of residual homoskedasticity (Breusch-Pagan $p = 0.0113$). The model exhibits no first-order autocorrelation (Durbin-Watson $DW = 1.737$) and safe variance inflation levels ($\text{VIF} < 8.5$).



| Market Shocks vs. Margins | Regression OLS Fit | Residual Diagnostics |
| --- | --- | --- |
|  |  |  |

---

## 2. System Architecture

The pipeline consists of three specialized Python modules:

1. **`ryanair_etl.py`**: Ingests unstructured IFRS quarterly disclosures (PDF), extracts financial statement rows via regular expressions, and solves fiscal calendar misalignments using mathematical quarterly decomposition ($\text{Q4} = \text{Full Year} - \text{9 Months}$)[cite: 2].
2. **`lufthansa_etl.py`**: Scans multi-tab Excel workbooks, dynamically locating Group segment reporting rows to extract Revenue, Operating Expenses, and Adjusted EBITDA across reporting framework shifts[cite: 3].
3. **`econometric_analysis.py`**: Loads the consolidated panel dataset (`airlines_data2020-2024.xls`, $N=40$), estimates the robust OLS regression model, generates high-resolution figures (300 DPI), and compiles an executive research report (`Airline_Hedging_Econometric_Report.docx`).



---

## 3. Data Ingestion & Curation Notice

A clear boundary is established between automated tabular extraction and operational metric curation:

* **Automated Extraction:** Core financial metrics (Operating Revenue, Operating Costs, Depreciation, and EBITDA) are extracted directly from corporate tables and text layers by the ETL engines[cite: 2, 3].
* **Manual Metric Verification (PLF & Hedge Ratio):** Key operational drivers—Passenger Load Factor (PLF) and Forward Fuel Hedge Ratios—are not standardized line items within primary IFRS financial tables[cite: 2, 3]. Because these metrics reside inside earnings presentation slide decks, derivative footnotes, and MD&A appendices, automated scraping introduces high error rates[cite: 2, 3]. These values were **manually sourced, reconciled against official quarterly earnings releases, and mapped directly into the code execution dictionaries**, guaranteeing 100% verified accuracy[cite: 2, 3].

---

## 4. File Requirements for Full Pipeline Reproduction

To run the full pipeline from raw corporate disclosures, download the primary documents from the respective Investor Relations portals and place them in the project root directory:

### A. Ryanair PDF Disclosures (`ryanair_etl.py`)

Requires the following 21 quarterly announcement PDFs from the Ryanair Investor Relations Results Centre:

* `Ryanair-FY20-Results.pdf`, `Ryanair-Q3-FY20-Results.pdf`, `Ryanair-Q1-FY21-Results.pdf`[cite: 2]
* `Ryanair-H1-FY21-Results.pdf`, `Ryanair-Q3-FY21-Results.pdf`, `Ryanair-FY21-Results.pdf`[cite: 2]
* `Ryanair-Q1-FY22-Results.pdf`, `Ryanair-H1-FY22-Results.pdf`, `Q3-FY22-Ryanair-Results.pdf`[cite: 2]
* `FY22-Ryanair-Results.pdf`, `Q1-FY23-Results.pdf`, `H1-FY23-Results.pdf`, `Ryanair-Q3-FY23-Results.pdf`[cite: 2]
* `FY23-Ryanair-Results.pdf`, `Q1-FY24-Ryanair-Results.pdf`, `H1-FY24-Ryanair-Results.pdf`, `Ryanair-Q3-FY24-Results.pdf`[cite: 2]
* `FY24-Ryanair-Results.pdf`, `Q1-FY25-Ryanair-Results.pdf`, `H1-FY25-Ryanair-Results.pdf`, `Q3-FY25-Ryanair-Results.pdf`[cite: 2]

```bash
python ryanair_etl.py

```

### B. Lufthansa Financial Workbooks (`lufthansa_etl.py`)

Requires the 5 annual financial statement Excel workbooks from the Lufthansa Group Investor Relations portal:

* `LH-AR-2020.xlsx`[cite: 3]
* `LH-AR-2021.xlsx`[cite: 3]
* `LH-AR-2022.xlsx`[cite: 3]
* `LH-AR-2023.xlsx`[cite: 3]
* `LH-AR-2024.xlsx`[cite: 3]

```bash
python lufthansa_etl.py

```

### C. Direct Econometric Execution (`econometric_analysis.py`)

**No raw file downloads required.** This script executes out-of-the-box using the pre-compiled, audit-ready dataset **`airlines_data2020-2024.xls`** already included in this repository.

```bash
python econometric_analysis.py

```

---

## 5. Quickstart

```bash
# Clone the repository
git clone https://github.com/JohnStononloan/airline-hedging-econometrics-etl.git
cd airline-hedging-econometrics-etl

# Install analytical environment
pip install -r requirements.txt

# Run econometric estimation and generate DOCX report
python econometric_analysis.py

```

---

## 6. Technical Stack

* **Programming Language:** Python 3.x
* **Data Processing:** `pandas`, `numpy`, `openpyxl`, `xlrd`[cite: 1, 2, 3]
* **Document Parsing & Regex:** `pdfplumber`, `re`[cite: 2]
* **Econometrics:** `statsmodels` (OLS with HC1 robust standard errors, Breusch-Pagan, VIF, Durbin-Watson)


* **Visualization & Reporting:** `matplotlib`, `seaborn`, `python-docx`


---

## Author

* **Maciej Klempka**
* Quantitative Analysis & Financial Workflow Automation
