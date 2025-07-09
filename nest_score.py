import pandas as pd
import numpy as np
from typing import Dict

# Configuration constants
SUBJECT_COLS = ['Bio Marks', 'Chem Marks', 'Math Marks', 'Phy Marks']
SMAS_MULTIPLIERS = {'GEN': 0.20, 'OBC': 0.18, 'SC': 0.10, 'ST': 0.10}
PERCENTILE_CUTOFFS = {'OBC': 90, 'SC': 75, 'ST': 75}


def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Load CSV and clean the data."""
    df = pd.read_csv(file_path)
    
    # Fill missing values
    df[SUBJECT_COLS] = df[SUBJECT_COLS].fillna(0).clip(lower=0)
    df['PWD-Status'] = df['PWD-Status'].fillna('No').str.strip().str.lower()
    df['JK-Status'] = df['JK-Status'].fillna('No').str.strip().str.lower()
    df['Category'] = df['Category'].fillna('GEN').str.upper()
    
    return df


def calculate_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total marks (best 3 of 4) and max subject mark."""
    marks = df[SUBJECT_COLS].values
    sorted_marks = np.sort(marks, axis=1)[:, ::-1]  # Sort descending
    
    df['Total Marks'] = sorted_marks[:, :3].sum(axis=1)  # Sum top 3
    df['Max Subject Mark'] = sorted_marks[:, 0]  # Highest mark
    df['Percentile'] = ((df['Total Marks'].rank(method='min') - 1) / len(df)) * 100
    
    return df


def calculate_smas(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Calculate Subject-wise Minimum Admissible Score."""
    smas = {}
    print("\n=== SMAS SCORES ACROSS CATEGORIES ===")
    
    for subject in SUBJECT_COLS:
        top_100_avg = df[subject].nlargest(100).mean()
        smas[subject] = {cat: mult * top_100_avg for cat, mult in SMAS_MULTIPLIERS.items()}
        
        # Print SMAS scores for this subject
        print(f"{subject}:")
        for category, score in smas[subject].items():
            print(f"  {category}: {score:.2f}")
    
    return smas


def check_smas_qualification(df: pd.DataFrame, smas: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Count qualified subjects for each candidate."""
    def count_qualified(row):
        category = row['Category'] if row['Category'] in SMAS_MULTIPLIERS else 'GEN'
        multiplier = 0.5 if row['PWD-Status'] == 'yes' else 1.0
        
        count = 0
        for subject in SUBJECT_COLS:
            threshold = smas[subject][category] * multiplier
            if row[subject] >= threshold:
                count += 1
        return count
    
    df['SMAS Qualified Subjects'] = df.apply(count_qualified, axis=1)
    return df


def assign_ranks(df: pd.DataFrame, mask: pd.Series, rank_col: str, prefix: str = "") -> pd.DataFrame:
    """Assign ranks to qualified candidates with tie-breaking."""
    if not mask.any():
        return df
    
    qualified = df[mask].copy()
    qualified = qualified.sort_values(['Total Marks', 'Max Subject Mark'], ascending=[False, False])
    
    # Calculate ranks with tie-breaking
    ranks = qualified['Total Marks'].rank(method='min', ascending=False)
    ties = qualified['Total Marks'].duplicated(keep=False)
    
    if ties.any():
        for total_mark, group in qualified[ties].groupby('Total Marks'):
            group_ranks = group['Max Subject Mark'].rank(method='min', ascending=False)
            base_rank = ranks.loc[group.index].min()
            ranks.loc[group.index] = base_rank + group_ranks - 1
    
    ranks = ranks.astype(int)
    if prefix:
        qualified[rank_col] = [f"{prefix}-{rank}" for rank in ranks]
    else:
        qualified[rank_col] = ranks
    
    df.loc[mask, rank_col] = qualified[rank_col]
    return df


def calculate_all_ranks(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all rank categories."""
    # Initialize rank columns
    for col in ['Gen-rank', 'Cat-rank', 'JK-rank', 'PWD-rank', 'EWS-rank']:
        df[col] = pd.NA
    
    # We'll print qualified category numbers after rank assignment
    
    # Qualification masks
    base_qual = (df['SMAS Qualified Subjects'] >= 3)
    
    masks = {
        'gen_basic': base_qual & (df['Percentile'] >= 95),
        'obc': base_qual & (df['Category'] == 'OBC') & (df['Percentile'] >= 90),
        'sc': base_qual & (df['Category'] == 'SC') & (df['Percentile'] >= 75),
        'st': base_qual & (df['Category'] == 'ST') & (df['Percentile'] >= 75),
        'pwd': base_qual & (df['PWD-Status'] == 'yes') & (df['Percentile'] >= 75),
        'ews': base_qual & df['Category'].str.contains('EWS', case=False, na=False) & (df['Percentile'] >= 95)
    }
    
    # General qualification combines all categories
    gen_qual = masks['gen_basic'] | masks['obc'] | masks['sc'] | masks['st'] | masks['pwd']
    masks['jk'] = (df['JK-Status'] == 'yes') & gen_qual
    
    # Assign ranks
    df = assign_ranks(df, gen_qual, 'Gen-rank')
    
    # Category ranks
    for category, cutoff in PERCENTILE_CUTOFFS.items():
        cat_mask = base_qual & (df['Category'] == category) & (df['Percentile'] >= cutoff)
        df = assign_ranks(df, cat_mask, 'Cat-rank', category)
    
    # Other ranks
    df = assign_ranks(df, masks['ews'], 'EWS-rank', 'EWS')
    df = assign_ranks(df, masks['pwd'], 'PWD-rank')
    df = assign_ranks(df, masks['jk'], 'JK-rank')
    
    return df


def process_exam_results(input_file: str = 'provisional.csv', output_file: str = 'results.csv') -> pd.DataFrame:
    """Main function to process exam results."""
    # Load and process data
    df = load_and_clean_data(input_file)
    df = calculate_scores(df)
    
    # Calculate SMAS and qualification
    smas = calculate_smas(df)
    df = check_smas_qualification(df, smas)
    
    # Calculate ranks
    df = calculate_all_ranks(df)
    
    # Round percentiles and save
    df['Percentile'] = df['Percentile'].round(4)
    df.to_csv(output_file, index=False)
    
    # Print summary
    print("\n=== FINAL SUMMARY ===")
    print(f"Total candidates processed: {len(df)}")
    print(f"General ranks assigned: {df['Gen-rank'].notna().sum()}")
    print(f"Category ranks assigned: {df['Cat-rank'].notna().sum()}")
    print(f"EWS ranks assigned: {df['EWS-rank'].notna().sum()}")
    print(f"PWD ranks assigned: {df['PWD-rank'].notna().sum()}")
    print(f"JK ranks assigned: {df['JK-rank'].notna().sum()}")
    
    # Print qualified candidates by category
    print("\n=== QUALIFIED CANDIDATES BY CATEGORY ===")
    qualified_mask = df['Gen-rank'].notna()
    qualified_df = df[qualified_mask]
    
    obc_qualified = (qualified_df['Category'] == 'OBC').sum()
    sc_qualified = (qualified_df['Category'] == 'SC').sum()
    st_qualified = (qualified_df['Category'] == 'ST').sum()
    gen_qualified = ((qualified_df['Category'] == 'GEN') | 
                    (~qualified_df['Category'].isin(['OBC', 'SC', 'ST']))).sum()
    print("\n=== FINAL SUMMARY ===")
    print(f"Total candidates : {len(df)}")
    print(f"Total Merit ranks : {df['Gen-rank'].notna().sum()}")
    print(f"Total Cat   ranks: {df['Cat-rank'].notna().sum()}")
    print(f"EWS : {df['EWS-rank'].notna().sum()}")
    print(f"PWD : {df['PWD-rank'].notna().sum()}")
    print(f"JK  : {df['JK-rank'].notna().sum()}")
    print(f"OBC : {obc_qualified}")
    print(f"SC  : {sc_qualified}")
    print(f"ST  : {st_qualified}")
    print(f"GEN : {gen_qualified}")
    print(f"Total qualified candidates: {qualified_df.shape[0]}")
    
    return df


# Usage
if __name__ == '__main__':
    results = process_exam_results('provisional.csv', 'output_results.csv')
