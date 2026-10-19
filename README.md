# Loan Default Analysis: Data Cleaning & EDA

Cleaning a LendingClub-style loan dataset and finding which loan and borrower factors are linked to default.

![Cleaning before and after](images/01_before_after_cleaning.png)

**Notebook:** [`loan_default_eda.ipynb`](loan_default_eda.ipynb) (all outputs and charts are included, so you can read it directly on GitHub)

## Data

- Raw file: `loan_train.csv`, **27,003 rows × 47 columns**
- After cleaning: **25,727 rows × 27 columns**
- Default rate: **14.5%** (3,719 of 25,727 loans)
- The data file is not included. See [`data/README.md`](data/README.md).

## Cleaning steps

1. **Inspected** shape, types, missing values, and duplicates.
2. **Dropped 21 columns:** identifiers (`id`, `member_id`, `url`), free text (`desc`, `emp_title`), and *leakage* columns, which are only known after the loan is issued (`total_pymnt`, `recoveries`, `out_prncp`, ...), so they would leak the outcome.
3. **Created flag columns** (`has_delinq`, `has_record`) for the two mostly-empty columns, instead of inventing values.
4. **Removed 1,276 rows (4.7%)** with missing `emp_length`, `pub_rec_bankruptcies`, `revol_util`, or `title`. The default rate barely changed (14.7% before, 14.5% after).
5. **Converted text to numbers:**
   - `int_rate`, `revol_util`: removed `%` (`int_rate_pct`, `revol_util_pct`)
   - `term`: removed the word "months" (`term_months`)
   - `emp_length`: "< 1 year" → 0, "10+ years" → 10
6. **Created `credit_history_years`** from `earliest_cr_line` and the loan issue date.
7. **Checked outliers** with the IQR rule and **skewness** of the numeric columns. The outliers were real values, so they were kept.

## Key findings

![Default rate by key factors](images/02_default_rate_key_factors.png)

- **Interest rate** is the strongest factor: default goes from 4.1% in the lowest group to 31% in the highest.
- **Loan term:** 60-month loans default at about 25% vs about 11% for 36-month loans.
- **Grade:** default rises from about 6% (A) to about 34% (G). Higher-risk grades also have fewer loans.
- **Purpose:** `small_business` loans are the riskiest (27%).
- **Income:** the lowest-income group defaults more (18.2%) than the highest (10.6%).
- **Public records** (23% vs 14%) and **credit inquiries in the last 6 months** are also linked to higher default.
- **Verified** borrowers default more than **Not Verified** ones (16.9% vs 12.5%), the opposite of what you might expect.
- Employment length, home ownership, and credit history length show little effect.

![Correlation with default](images/03_correlation_with_default.png)

> These results show relationships in the data, not proof of cause.

## How to run

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the data file (see [`data/README.md`](data/README.md)) and put `loan_train.csv` in the same folder as the notebook.
3. Open `loan_default_eda.ipynb` with Jupyter or VS Code and run all cells.
4. (Optional) `python make_figures.py` re-creates the charts in `images/`.

## Skills used

- **Data cleaning:** missing values, duplicates, converting text to numbers, date handling, removing leakage columns
- **Outliers:** IQR rule, box plots, skewness check
- **Analysis:** default rate by feature, correlations
- **Tools:** Python, pandas, NumPy, matplotlib, seaborn

## Author

[Your name], Data Analytics student, Faculty of Computers and Information.

> This is a practice project on a public dataset, not client work.
