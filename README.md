# consumer-complaints-electricity-quality
Analyzing the relationship between consumer complaints and electricity supply quality using Python, SQL, and statistical analysis.

## Overview

An end-to-end data analytics case study investigating the relationship between consumer complaints and electricity supply quality in Brazil.

The project combines publicly available data from the Brazilian Electricity Regulatory Agency (ANEEL), including consumer complaints and electricity continuity indicators (DEC and FEC).

The analysis focuses on identifying patterns, statistical relationships, and actionable insights through data preparation, exploratory analysis, and statistical methods.

## Business Question

**Is there a statistically significant relationship between consumer complaints and electricity supply quality?**

## Key Questions

- Are consumer complaints associated with DEC and FEC indicators?
- How do complaint patterns vary across distribution companies?
- How do electricity quality indicators change over time?
- Are changes in DEC and FEC associated with subsequent changes in complaints?
- Which patterns could support service-quality improvement?

## Data Sources

The analysis uses two ANEEL public datasets:

- **Consumer Complaints — 1st and 2nd Level**
- **Collective Continuity Indicators — DEC and FEC**

The datasets are integrated using the distribution company's **CNPJ** and the corresponding **monthly reference period**.

## Methodology

The project follows an analytical workflow:

**Data Preparation → Data Validation → Exploratory Analysis → Statistical Analysis → Insights → Recommendations**

Key techniques include:

- Data cleaning and transformation
- Data validation and quality checks
- Descriptive statistics
- Correlation analysis
- Pearson and Spearman correlation
- Statistical significance testing
- Outlier analysis
- Temporal analysis
- Lagged relationship analysis
- Distribution company comparisons

## Expected Insights

The analysis aims to determine whether variations in electricity supply quality are associated with changes in consumer complaints and whether these relationships differ across distribution companies or over time.

> Correlation will be interpreted as an association and not as evidence of causation.

## Technologies

- Python
- Pandas
- NumPy
- SciPy
- Matplotlib
- SQL
- Jupyter Notebook
- Git & GitHub

## Project Structure

```text
consumer-complaints-electricity-quality/
│
├── README.md
│
├── data/
│   └── data_dictionary.md
│
├── notebooks/
│   ├── 01_data_preparation.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   └── 03_statistical_analysis.ipynb
│
├── sql/
│   ├── data_validation.sql
│   └── analytical_queries.sql
│
└── report/
    └── analytical_report.pdf
