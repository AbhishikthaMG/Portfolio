/* =============================================================================
Script: Upstream vs. Downstream Validation
Purpose: Compares transaction systems against reporting datasets to find 
         reconciliation inconsistencies.
=============================================================================
*/

WITH Upstream_Transactions AS (
    SELECT 
        Transaction_ID,
        Account_ID,
        Transaction_Amount,
        Transaction_Date
    FROM DB_SOURCE.UPSTREAM_SYSTEM
    WHERE Transaction_Date >= CURRENT_DATE - 30
),

Downstream_Reports AS (
    SELECT 
        Reporting_ID AS Transaction_ID,
        Account_Ref AS Account_ID,
        Reported_Amount AS Transaction_Amount,
        Report_Date
    FROM DB_WAREHOUSE.DOWNSTREAM_REPORTING
    WHERE Report_Date >= CURRENT_DATE - 30
)

-- Anomaly Detection Check
SELECT 
    u.Transaction_ID,
    u.Account_ID,
    u.Transaction_Amount AS Upstream_Amount,
    d.Transaction_Amount AS Downstream_Amount,
    (u.Transaction_Amount - COALESCE(d.Transaction_Amount, 0)) AS Variance_Amount,
    CASE 
        WHEN d.Transaction_ID IS NULL THEN 'Missing in Downstream Report'
        WHEN u.Transaction_Amount != d.Transaction_Amount THEN 'Amount Mismatch Exception'
        ELSE 'Fully Reconciled'
    END AS Reconciliation_Status
FROM Upstream_Transactions u
LEFT JOIN Downstream_Reports d ON u.Transaction_ID = d.Transaction_ID
WHERE u.Transaction_Amount != COALESCE(d.Transaction_Amount, 0) 
   OR d.Transaction_ID IS NULL;
