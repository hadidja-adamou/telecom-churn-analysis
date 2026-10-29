-- ============================================================
-- Telco churn: first-pass business questions (SQLite)
-- Expects data/processed/telco_clean.csv loaded into a table called `customers`. 
-- Column names match the cleaned dataset (see src/data_loading.py).
--
-- Format: every query starts with a numbered comment (1., 2., ...).
-- The notebook splits this file on those headers, so keep the pattern when adding a query.
-- ============================================================

-- 1. Overall churn rate
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churners,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers;

-- 2. Churn rate by contract type
SELECT
    contract,
    COUNT(*) AS num_customers,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- 3. Churn rate by tenure bucket
-- Buckets start inclusive: tenure = 12 falls in "12-23 months".
-- They are narrower early on, where most of the churn happens.
SELECT
    CASE
        WHEN tenure < 12 THEN '0-11 months'
        WHEN tenure < 24 THEN '12-23 months'
        WHEN tenure < 48 THEN '24-47 months'
        ELSE '48+ months'
    END AS tenure_bucket,
    COUNT(*) AS num_customers,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY tenure_bucket
ORDER BY MIN(tenure);

-- 4. Churn rate by payment method
SELECT
    paymentmethod,
    COUNT(*) AS num_customers,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY paymentmethod
ORDER BY churn_rate_pct DESC;

-- 5. Churn rate by online security and tech support status
-- "No internet service" is its own group: those customers cannot
-- subscribe to either add-on, so it does not mean "unprotected".
SELECT
    onlinesecurity,
    techsupport,
    COUNT(*) AS num_customers,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY onlinesecurity, techsupport
ORDER BY churn_rate_pct DESC;

-- 6. Average monthly charges: churned vs. retained
SELECT
    churn,
    ROUND(AVG(monthlycharges), 2) AS avg_monthly_charges,
    COUNT(*) AS num_customers
FROM customers
GROUP BY churn
ORDER BY churn;

-- 7. Priority risk segment: month-to-month + under 12 months + electronic check
-- Stacks the riskiest group from queries 2, 3 and 4. The tenure
-- threshold matches the first bucket of query 3.
SELECT
    COUNT(*) AS segment_size,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS pct_of_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churners,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END)
          / (SELECT COUNT(*) FROM customers WHERE churn = 'Yes'), 2) AS pct_of_all_churners
FROM customers
WHERE contract = 'Month-to-month'
  AND tenure < 12
  AND paymentmethod = 'Electronic check';