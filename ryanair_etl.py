import os
import re
import pdfplumber
import pandas as pd

# Environment setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_path(filename):
    return os.path.join(BASE_DIR, filename)


def extract_financial_amounts(line):
    """Extracts monetary figures from an IFRS statement row, filtering out percentage figures."""
    cleaned = re.sub(r"[+-]?\d+%", "", line)
    tokens = re.findall(r"\(?[\d,]+\.\d+\)?|\(?[\d,]+\)?", cleaned)
    nums = []
    for t in tokens:
        neg = t.startswith("(") and t.endswith(")")
        c = t.replace("(", "").replace(")", "").replace(",", "").strip()
        try:
            val = float(c)
            nums.append(-val if neg else val)
        except ValueError:
            pass
    return nums


def extract_income_statement(file_path, markers):
    """Scans a PDF file searching for the target income statement table using header markers."""
    rev, costs, depr = 0.0, 0.0, 0.0
    target_text = ""

    full_path = get_path(file_path)
    if not os.path.exists(full_path):
        print(f"[!] FILE NOT FOUND IN DIRECTORY: {file_path}")
        return 0.0, 0.0, 0.0

    if isinstance(markers, str):
        markers = [markers]

    with pdfplumber.open(full_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            normalized_t = " ".join(t.split())
            found = False
            for m in markers:
                if re.search(m, normalized_t, re.IGNORECASE):
                    target_text = t
                    found = True
                    break
            if found:
                break

    if not target_text:
        print(f"[!] TABLE NOT DETECTED in file: {file_path}")
        return 0.0, 0.0, 0.0

    for line in target_text.split("\n"):
        if "Total operating revenues" in line and rev == 0:
            nums = [n for n in extract_financial_amounts(line) if n > 100]
            if nums:
                rev = nums[0]
        if "Total operating expenses" in line and costs == 0:
            nums = [n for n in extract_financial_amounts(line) if n > 100]
            if nums:
                costs = nums[0]
        if line.strip().startswith("Depreciation") and depr == 0:
            nums = [n for n in extract_financial_amounts(line) if n > 50]
            if nums:
                depr = nums[0]

    return rev, costs, depr


# ==============================================================================
# EXECUTION MATRIX (PIPELINE 2020-2024) - PRESERVING EXACT SOURCE FILENAMES
# ==============================================================================

PIPELINE = [
    # 2020
    {"q": "2020 Q1", "method": "Decomposition (FY-9M)", "type": "diff", "f1": "Ryanair-FY20-Results.pdf", "m1": r"Year Ended Mar(?:ch)? 31",
     "f2": "Ryanair-Q3-FY20-Results.pdf", "m2": r"(?:9|Nine) Months Ended Dec(?:ember)? 31", "plf": 0.95, "hedge": 0.90},
    {"q": "2020 Q2", "method": "Direct (Q1 FY)", "type": "direct", "f1": "Ryanair-Q1-FY21-Results.pdf",
     "m1": r"Quarter Ended Jun(?:e)? 30", "plf": 0.61, "hedge": 0.37},
    {"q": "2020 Q3", "method": "Quarterly Table (H1 FY)", "type": "direct", "f1": "Ryanair-H1-FY21-Results.pdf",
     "m1": r"Quarter ended Sep(?:tember)? 30", "plf": 0.72, "hedge": 0.37},
    {"q": "2020 Q4", "method": "Quarterly Table (Q3 FY)", "type": "direct", "f1": "Ryanair-Q3-FY21-Results.pdf", "m1": [
        r"Quarter ended Dec(?:ember)? 31", r"Q3 Dec 31"], "plf": 0.70, "hedge": 0.37},
    # 2021
    {"q": "2021 Q1", "method": "Decomposition (FY-9M)", "type": "diff", "f1": "Ryanair-FY21-Results.pdf", "m1": r"Year Ended Mar(?:ch)? 31",
     "f2": "Ryanair-Q3-FY21-Results.pdf", "m2": r"(?:9|Nine) Months Ended Dec(?:ember)? 31", "plf": 0.71, "hedge": 0.37},
    {"q": "2021 Q2", "method": "Direct (Q1 FY)", "type": "direct", "f1": "Ryanair-Q1-FY22-Results.pdf",
     "m1": r"Quarter Ended Jun(?:e)? 30", "plf": 0.73, "hedge": 0.50},
    {"q": "2021 Q3", "method": "Quarterly Table (H1 FY)", "type": "direct", "f1": "Ryanair-H1-FY22-Results.pdf",
     "m1": r"Quarter Ended Sep(?:tember)? 30", "plf": 0.79, "hedge": 0.55},
    {"q": "2021 Q4", "method": "Quarterly Table (Q3 FY)", "type": "direct", "f1": "Q3-FY22-Ryanair-Results.pdf", "m1": [
        r"Quarter Ended Dec(?:ember)? 31", r"Q3 Dec 31"], "plf": 0.84, "hedge": 0.60},
    # 2022
    {"q": "2022 Q1", "method": "Decomposition (FY-9M)", "type": "diff", "f1": "FY22-Ryanair-Results.pdf", "m1": r"Year Ended Mar(?:ch)? 31",
     "f2": "Q3-FY22-Ryanair-Results.pdf", "m2": r"(?:9|Nine) Months Ended Dec(?:ember)? 31", "plf": 0.82, "hedge": 0.80},
    {"q": "2022 Q2", "method": "Direct (Q1 FY)", "type": "direct", "f1": "Q1-FY23-Results.pdf",
     "m1": r"Quarter Ended Jun(?:e)? 30", "plf": 0.92, "hedge": 0.80},
    {"q": "2022 Q3", "method": "Quarterly Table (H1 FY)", "type": "direct", "f1": "H1-FY23-Results.pdf",
     "m1": r"Quarter Ended Sep(?:tember)? 30", "plf": 0.94, "hedge": 0.80},
    {"q": "2022 Q4", "method": "Quarterly Table (Q3 FY)", "type": "direct", "f1": "Ryanair-Q3-FY23-Results.pdf", "m1": [
        r"Quarter Ended Dec(?:ember)? 31", r"Q3 Dec 31"], "plf": 0.93, "hedge": 0.80},
    # 2023
    {"q": "2023 Q1", "method": "Decomposition (FY-9M)", "type": "diff", "f1": "FY23-Ryanair-Results.pdf", "m1": r"Year Ended Mar(?:ch)? 31",
     "f2": "Ryanair-Q3-FY23-Results.pdf", "m2": r"(?:9|Nine) Months Ended Dec(?:ember)? 31", "plf": 0.93, "hedge": 0.80},
    {"q": "2023 Q2", "method": "Direct (Q1 FY)", "type": "direct", "f1": "Q1-FY24-Ryanair-Results.pdf",
     "m1": r"Quarter Ended Jun(?:e)? 30", "plf": 0.95, "hedge": 0.80},
    {"q": "2023 Q3", "method": "Quarterly Table (H1 FY)", "type": "direct", "f1": "H1-FY24-Ryanair-Results.pdf",
     "m1": r"Quarter Ended Sep(?:tember)? 30", "plf": 0.95, "hedge": 0.80},
    {"q": "2023 Q4", "method": "Quarterly Table (Q3 FY)", "type": "direct", "f1": "Ryanair-Q3-FY24-Results.pdf", "m1": [
        r"Quarter Ended December 31,\s*2023", r"Quarter Ended Dec"], "plf": 0.93, "hedge": 0.94},
    # 2024
    {"q": "2024 Q1", "method": "Decomposition (FY-9M)", "type": "diff", "f1": "FY24-Ryanair-Results.pdf", "m1": r"Year\s+Ended\s+Mar(?:ch)?\s+31",
     "f2": "Ryanair-Q3-FY24-Results.pdf", "m2": r"(?:9|Nine)\s+Months\s+Ended\s+Dec(?:ember)?\s+31", "plf": 0.94, "hedge": 0.94},
    {"q": "2024 Q2", "method": "Direct (Q1 FY)", "type": "direct", "f1": "Q1-FY25-Ryanair-Results.pdf",
     "m1": r"Quarter Ended Jun(?:e)? 30", "plf": 0.94, "hedge": 0.75},
    {"q": "2024 Q3", "method": "Quarterly Table (H1 FY)", "type": "direct", "f1": "H1-FY25-Ryanair-Results.pdf",
     "m1": r"Quarter Ended Sep(?:tember)? 30", "plf": 0.96, "hedge": 0.77},
    {"q": "2024 Q4", "method": "Quarterly Table (Q3 FY)", "type": "direct", "f1": "Q3-FY25-Ryanair-Results.pdf", "m1": [
        r"Quarter Ended Dec(?:ember)? 31", r"Q3 Dec 31"], "plf": 0.92, "hedge": 0.78}
]

# ==============================================================================
# PIPELINE EXECUTION ENGINE
# ==============================================================================

if __name__ == "__main__":
    print("[*] Initializing PDF financial data extraction engine...")
    results = []

    for idx, cfg in enumerate(PIPELINE, 1):
        print(f"[{idx}/20] Processing: {cfg['q']}...")

        # Fallback for Ryanair-Q3-FY24-Results.pdf with corrupted font encoding
        if cfg["q"] == "2023 Q4":
            rev, costs, depr = 2698.7, 2717.6, 263.4
        elif cfg["q"] == "2024 Q1":
            # FY24 (dynamically extracted) minus 9M FY24 (manual entry due to broken fonts in 9M filing)
            rev_fy, costs_fy, depr_fy = extract_income_statement(
                cfg["f1"], cfg["m1"])
            rev_9m, costs_9m, depr_9m = 11273.9, 8877.0, 822.2
            rev = rev_fy - rev_9m
            costs = costs_fy - costs_9m
            depr = depr_fy - depr_9m
        elif cfg["type"] == "diff":
            rev_fy, costs_fy, depr_fy = extract_income_statement(
                cfg["f1"], cfg["m1"])
            rev_9m, costs_9m, depr_9m = extract_income_statement(
                cfg["f2"], cfg["m2"])
            rev = rev_fy - rev_9m
            costs = costs_fy - costs_9m
            depr = depr_fy - depr_9m
        elif cfg["type"] == "direct":
            rev, costs, depr = extract_income_statement(cfg["f1"], cfg["m1"])

        ebitda = (rev - costs) + depr
        margin = ebitda / rev if rev != 0 else 0

        results.append([cfg["q"], cfg["method"], rev, costs,
                       depr, ebitda, margin, cfg["plf"], cfg["hedge"]])

    columns = [
        "Quarter", "Method", "Revenue (EUR m)", "Op. Costs (EUR m)",
        "Depreciation (EUR m)", "EBITDA (EUR m)", "EBITDA Margin",
        "PLF", "Hedge Ratio"
    ]

    df = pd.DataFrame(results, columns=columns)
    df = df.round({
        "Revenue (EUR m)": 1, "Op. Costs (EUR m)": 1, "Depreciation (EUR m)": 1,
        "EBITDA (EUR m)": 1, "EBITDA Margin": 3, "PLF": 2, "Hedge Ratio": 2
    })

    print("\n" + "="*85)
    print(" RYANAIR OPERATIONAL & FINANCIAL PANEL DATA (2020-2024)")
    print("="*85)
    print(df.to_string(index=False))

    excel_path = os.path.join(BASE_DIR, "ryanair_panel_2020_2024.xlsx")
    df.to_excel(excel_path, index=False, sheet_name="Financial Data")
    print(f"\n[V] Excel file successfully generated: {excel_path}")
