"""Exploratory trends and correlations. Run after src.prepare_data."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from src.config import PROCESSED_DIR, OUTPUTS_DIR


def correlation(x, y):
    """Return Pearson and Spearman statistics after pairwise missing-value removal."""
    pair = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(pair) < 3 or pair.x.nunique() < 2 or pair.y.nunique() < 2:
        return {"n": len(pair), "pearson_r": np.nan, "pearson_p": np.nan,
                "spearman_rho": np.nan, "spearman_p": np.nan}
    pr, pp = pearsonr(pair.x, pair.y)
    sr, sp = spearmanr(pair.x, pair.y)
    return {"n": len(pair), "pearson_r": pr, "pearson_p": pp,
            "spearman_rho": sr, "spearman_p": sp}


def main():
    path = PROCESSED_DIR / "analytical_distributor_month.csv"
    if not path.exists():
        raise FileNotFoundError("Run `python -m src.prepare_data` first.")
    df = pd.read_csv(path)
    metrics = ["total_manifestations_received", "total_manifestations_procedent",
               "procedent_rate", "DEC_unweighted_mean_proxy", "FEC_unweighted_mean_proxy"]
    for col in metrics:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    pairs = [
        ("total_manifestations_received", "DEC_unweighted_mean_proxy"),
        ("total_manifestations_received", "FEC_unweighted_mean_proxy"),
        ("total_manifestations_procedent", "DEC_unweighted_mean_proxy"),
        ("total_manifestations_procedent", "FEC_unweighted_mean_proxy"),
        ("procedent_rate", "DEC_unweighted_mean_proxy"),
        ("procedent_rate", "FEC_unweighted_mean_proxy")
    ]
    results = []
    for x, y in pairs:
        stats = correlation(df[x], df[y])
        stats.update({"x_variable": x, "y_variable": y})
        results.append(stats)
    pd.DataFrame(results).to_csv(OUTPUTS_DIR / "correlation_results.csv", index=False)

    trends = (df.groupby("year_month", as_index=False)
              .agg(total_manifestations=("total_manifestations_received", "sum"),
                   mean_dec_proxy=("DEC_unweighted_mean_proxy", "mean"),
                   mean_fec_proxy=("FEC_unweighted_mean_proxy", "mean"),
                   distributors=("cnpj", "nunique"))
              .sort_values("year_month"))
    trends.to_csv(OUTPUTS_DIR / "monthly_trends.csv", index=False)

    for y, filename, title in [
        ("DEC_unweighted_mean_proxy", "complaints_vs_dec.png", "Manifestations vs DEC proxy"),
        ("FEC_unweighted_mean_proxy", "complaints_vs_fec.png", "Manifestations vs FEC proxy")
    ]:
        plot = df[["total_manifestations_received", y]].dropna()
        if not plot.empty:
            plt.figure(figsize=(8, 5))
            plt.scatter(plot["total_manifestations_received"], plot[y], alpha=0.6)
            plt.xlabel("Total manifestations received")
            plt.ylabel(y.replace("_", " "))
            plt.title(title)
            plt.tight_layout()
            plt.savefig(OUTPUTS_DIR / filename, dpi=150)
            plt.close()

    print("Analysis complete. See outputs/correlation_results.csv and monthly_trends.csv.")
    print("Interpret correlations as associations, not causal effects.")
    print("DEC/FEC columns are unweighted set-level proxies, not official aggregates.")


if __name__ == "__main__":
    main()
