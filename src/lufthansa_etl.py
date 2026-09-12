import glob
import pandas as pd

LH_METRICS = {
    "Q1 2020": {"LH_PLF": 0.733, "LH_Hedge_Ratio": 0.73},
    "Q2 2020": {"LH_PLF": 0.560, "LH_Hedge_Ratio": 0.73},
    "Q3 2020": {"LH_PLF": 0.530, "LH_Hedge_Ratio": 0.73},
    "Q4 2020": {"LH_PLF": 0.430, "LH_Hedge_Ratio": 0.73},
    "Q1 2021": {"LH_PLF": 0.450, "LH_Hedge_Ratio": 0.36},
    "Q2 2021": {"LH_PLF": 0.514, "LH_Hedge_Ratio": 0.44},
    "Q3 2021": {"LH_PLF": 0.688, "LH_Hedge_Ratio": 0.52},
    "Q4 2021": {"LH_PLF": 0.655, "LH_Hedge_Ratio": 0.60},
    "Q1 2022": {"LH_PLF": 0.654, "LH_Hedge_Ratio": 0.74},
    "Q2 2022": {"LH_PLF": 0.802, "LH_Hedge_Ratio": 0.65},
    "Q3 2022": {"LH_PLF": 0.861, "LH_Hedge_Ratio": 0.68},
    "Q4 2022": {"LH_PLF": 0.820, "LH_Hedge_Ratio": 0.64},
    "Q1 2023": {"LH_PLF": 0.797, "LH_Hedge_Ratio": 0.70},
    "Q2 2023": {"LH_PLF": 0.832, "LH_Hedge_Ratio": 0.83},
    "Q3 2023": {"LH_PLF": 0.862, "LH_Hedge_Ratio": 0.86},
    "Q4 2023": {"LH_PLF": 0.813, "LH_Hedge_Ratio": 0.86},
    "Q1 2024": {"LH_PLF": 0.797, "LH_Hedge_Ratio": 0.85},
    "Q2 2024": {"LH_PLF": 0.822, "LH_Hedge_Ratio": 0.84},
    "Q3 2024": {"LH_PLF": 0.872, "LH_Hedge_Ratio": 0.82},
    "Q4 2024": {"LH_PLF": 0.822, "LH_Hedge_Ratio": 0.83}
}

years = [2020, 2021, 2022, 2023, 2024]
results = []

for year in years:
    pattern = f"*LH-AR-{year}*.xls*"
    matched_files = glob.glob(pattern)

    if not matched_files:
        continue

    file_path = matched_files[0]
    xls = pd.ExcelFile(file_path)

    for q_num in [1, 2, 3, 4]:
        q_prefix = f"Q{q_num}"
        sheet_matches = [
            s for s in xls.sheet_names if s.strip().startswith(q_prefix)]

        if not sheet_matches:
            continue

        sheet_name = sheet_matches[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)

        lh_col_idx = None
        for r in range(min(6, len(df))):
            for c, val in enumerate(df.iloc[r]):
                if isinstance(val, str) and "LH GROUP" in val.upper():
                    lh_col_idx = c
                    break
            if lh_col_idx is not None:
                break

        rev = None
        ebitda = None
        opex = None

        for _, row in df.iterrows():
            row_str = " ".join([str(x) for x in row.values])

            if "Total Revenue" in row_str:
                rev = row.iloc[lh_col_idx] if lh_col_idx is not None else row.iloc[-3]
                if pd.isna(rev) or str(rev).strip() in ["", "nan"]:
                    rev = row.iloc[-3]

            if "Operating Expenses" in row_str:
                opex = row.iloc[lh_col_idx] if lh_col_idx is not None else row.iloc[-3]
                if pd.isna(opex) or str(opex).strip() in ["", "nan"]:
                    opex = row.iloc[-3]

            if "Adjusted EBITDA" in row_str or ("EBITDA" in row_str and ebitda is None):
                ebitda = row.iloc[lh_col_idx] if lh_col_idx is not None else row.iloc[-3]
                if pd.isna(ebitda) or str(ebitda).strip() in ["", "nan"]:
                    ebitda = row.iloc[-3]

        key = f"Q{q_num} {year}"
        metrics = LH_METRICS.get(key, {"LH_PLF": None, "LH_Hedge_Ratio": None})

        try:
            rev = float(rev)
            ebitda = float(ebitda)
            opex = float(opex) if opex is not None else None

            # Usunięto mnożenie przez 100, wynik jako ułamek
            margin = (ebitda / rev) if rev != 0 else 0.0

            results.append({
                "Year": year,
                "Quarter": key,
                "Revenues (EUR m)": rev,
                "Expenses ( EUR m)": opex,
                "EBITDA (EUR m)": ebitda,
                " EBITDA margin": round(margin, 4),
                "LH_PLF": metrics["LH_PLF"],
                "LH_Hedge_Ratio": metrics["LH_Hedge_Ratio"]
            })
        except Exception:
            pass

df_results = pd.DataFrame(results)

# Wyświetla wyniki w terminalu
print(df_results.to_string(index=False))

# Generuje plik Excel z danymi
output_file = "Lufthansa_ETL_Wyniki.xlsx"
df_results.to_excel(output_file, index=False)
print(f"\nDane pomyślnie zapisano do pliku: {output_file}")
