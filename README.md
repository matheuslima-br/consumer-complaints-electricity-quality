# Consumer Complaints & Electricity Supply Quality

## Business problem
Consumer manifestations and electricity continuity indicators are published in separate ANEEL datasets. This project investigates whether monthly consumer manifestations are associated with electricity supply continuity (DEC and FEC) across distributors.

**Main question:** Are higher manifestation volumes associated with worse electricity supply continuity?

This is an observational analysis. Correlation does not establish causation.

## Data
Place these original files in `data/raw/`:
- `indicadores-continuidade-coletivos-2020-2029.csv`
- `manifestacoes-1-2-niveis-distribuidora-2025.csv`

Source: [ANEEL Open Data Portal](https://dadosabertos.aneel.gov.br/). Raw files are not included in this repository.

## Method
1. Inspect and validate the source files.
2. Standardize CNPJ and monthly reference.
3. Aggregate manifestations by distributor and month.
4. Select only consolidated `DEC` and `FEC` rows.
5. Summarize set-level DEC/FEC as an **unweighted mean proxy**.
6. Join both datasets by CNPJ and year-month.
7. Explore trends and calculate Pearson and Spearman correlations.
8. Interpret findings and develop evidence-based proposals.

## Important methodological limitation
The continuity file contains records by `IdeConjUndConsumidoras` (consumer-unit set). A simple mean across sets is **not necessarily the official distributor-level DEC/FEC**. A valid weighted aggregation may require the number of consumer units or another ANEEL-prescribed weighting variable, which is not among the columns inspected so far.

The generated fields `DEC_unweighted_mean_proxy` and `FEC_unweighted_mean_proxy` are exploratory proxies only. Do not describe them as official distributor-level indicators. Verify the applicable ANEEL methodology and obtain required weighting data or an official distributor-level series before definitive conclusions.

The manifestations dataset is for 2025, so the joined analysis is limited to overlapping months in 2025.

## Business problem, analytical solution and proposals
**Problem:** the two datasets have different structures and are not immediately comparable.

**Solution:** standardize company identifiers and monthly periods, aggregate manifestations at distributor-month level, prepare continuity indicators transparently, validate the join, and test statistical associations.

**Potential proposals, subject to findings:**
- Investigate distributor-months with both high manifestation volume and poor continuity.
- Separate supply-quality manifestations from billing, service, and other categories using a reviewed ANEEL code dictionary.
- Monitor received manifestations, procedent manifestations, procedent rate, DEC and FEC together.
- Investigate persistent or lagged patterns before recommending operational interventions.
- Improve outage communication and post-restoration communication if evidence supports this action.

These are hypotheses, not findings. Final recommendations must be supported by actual results.

## Run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m src.prepare_data
python -m src.analyze
```

## Outputs
- `data/processed/complaints_distributor_month.csv`
- `data/processed/complaints_by_code_distributor_month.csv`
- `data/processed/continuity_distributor_month_proxy.csv`
- `data/processed/analytical_distributor_month.csv`
- `outputs/data_quality_report.txt`
- `outputs/correlation_results.csv`
- `outputs/monthly_trends.csv`
- scatter plots in `outputs/`

## Limitations
- Complaint data covers 2025; continuity data spans 2020–2029.
- Set-level DEC/FEC cannot automatically be converted into official distributor-level metrics without a validated aggregation method.
- Complaint volume is influenced by customer base, access to reporting channels, awareness, and other factors.
- Monthly association does not prove causality.
- Missing values, duplicates, and source-definition changes must be assessed.
