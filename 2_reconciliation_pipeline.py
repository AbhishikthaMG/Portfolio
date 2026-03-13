"""
Script: Automated Reconciliation Pipeline
Purpose: Standardizes data cleansing and reconciliation logic across 
         reporting pipelines to reduce manual preparation time.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def run_reconciliation(upstream_path, downstream_path):
    print(f"[{datetime.now()}] Starting reporting automation pipeline...")
    
    # 1. Load operational records (Simulating the 1.2M+ records)
    df_upstream = pd.read_csv(upstream_path)
    df_downstream = pd.read_csv(downstream_path)

    # 2. Standardize data cleansing
    df_upstream['Transaction_Amount'] = pd.to_numeric(df_upstream['Transaction_Amount'], errors='coerce').fillna(0)
    df_downstream['Reported_Amount'] = pd.to_numeric(df_downstream['Reported_Amount'], errors='coerce').fillna(0)

    # 3. Merge datasets for comparison
    df_reconciled = pd.merge(
        df_upstream, 
        df_downstream, 
        left_on='Transaction_ID', 
        right_on='Reporting_ID', 
        how='outer', 
        indicator=True
    )

    # 4. Apply Reconciliation Logic
    conditions = [
        (df_reconciled['_merge'] == 'left_only'),
        (df_reconciled['_merge'] == 'right_only'),
        (df_reconciled['Transaction_Amount'] != df_reconciled['Reported_Amount'])
    ]
    choices = ['Missing Downstream', 'Orphaned Downstream', 'Amount Mismatch']
    
    df_reconciled['Data_Integrity_Issue'] = np.select(conditions, choices, default='Clean')

    # 5. Extract anomalies for the Power BI Dashboard
    exceptions = df_reconciled[df_reconciled['Data_Integrity_Issue'] != 'Clean']
    exceptions.to_csv('daily_reconciliation_exceptions.csv', index=False)
    
    print(f"[{datetime.now()}] Pipeline complete. Generated exception report with {len(exceptions)} flagged records.")

# run_reconciliation('upstream_data.csv', 'downstream_data.csv')
