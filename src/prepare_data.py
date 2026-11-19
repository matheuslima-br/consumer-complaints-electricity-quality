"""Prepare ANEEL datasets. Run: python -m src.prepare_data"""
import csv
from pathlib import Path
import pandas as pd
from src.config import CONTINUITY_FILE, COMPLAINTS_FILE, PROCESSED_DIR, OUTPUTS_DIR


def read_aneel_csv(path: Path) -> pd.DataFrame:
    """Detect delimiter and initially read columns as text to preserve IDs."""
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}. Put the CSV in data/raw/.")
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        sample = f.read(10000)
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except csv.Error:
        delimiter = ";"
    return pd.read_csv(path, sep=delimiter, dtype=str, encoding="utf-8-sig",
                       low_memory=False)


def clean_cnpj(series: pd.Series) -> pd.Series:
    """Normalize CNPJ to 14 digit characters."""
    value = series.astype("string").str.replace(r"\D", "", regex=True)
    value = value.mask(value.eq(""), pd.NA)
    return value.str.zfill(14)


def number_br(series: pd.Series) -> pd.Series:
    """Convert Brazilian decimal strings such as ',78' and '1,38' to numbers."""
    value = series.astype("string").str.strip()
    value = value.str.replace(".", "", regex=False)  # Brazilian thousands separator
    value = value.str.replace(",", ".", regex=False)
    value = value.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return pd.to_numeric(value, errors="coerce")


def year_month(year: pd.Series, month: pd.Series) -> pd.Series:
    """Build YYYY-MM while rejecting invalid months."""
    y = pd.to_numeric(year, errors="coerce")
    m = pd.to_numeric(month, errors="coerce")
    valid = y.notna() & m.between(1, 12)
    result = pd.Series(pd.NA, index=year.index, dtype="string")
    result.loc[valid] = (y.loc[valid].astype(int).astype(str) + "-" +
                         m.loc[valid].astype(int).astype(str).str.zfill(2))
    return result


def main():
    print("Reading source CSV files...")
    continuity = read_aneel_csv(CONTINUITY_FILE)
    manifestations = read_aneel_csv(COMPLAINTS_FILE)

    required_c = {"NumCNPJ", "SigIndicador", "AnoIndice", "NumPeriodoIndice",
                  "VlrIndiceEnviado", "IdeConjUndConsumidoras"}
    required_m = {"NumCPFCNPJ", "AnoCompetencia", "MesCompetencia",
                  "CodTipoManifestacao", "QtdManifestacoesRecebidas",
                  "QtdManifestacoesProcedentes"}
    if required_c - set(continuity.columns):
        raise ValueError(f"Continuity columns missing: {sorted(required_c-set(continuity.columns))}")
    if required_m - set(manifestations.columns):
        raise ValueError(f"Manifestation columns missing: {sorted(required_m-set(manifestations.columns))}")

    print(f"Continuity rows: {len(continuity):,}; manifestation rows: {len(manifestations):,}")

    # Prepare continuity at the consumer-unit-set level first.
    continuity["cnpj"] = clean_cnpj(continuity["NumCNPJ"])
    continuity["year_month"] = year_month(continuity["AnoIndice"], continuity["NumPeriodoIndice"])
    continuity["indicator"] = continuity["SigIndicador"].str.strip().str.upper()
    continuity["indicator_value"] = number_br(continuity["VlrIndiceEnviado"])

    # Exclude component indicators: retain only the exact consolidated codes.
    main = continuity[continuity["indicator"].isin(["DEC", "FEC"])].copy()
    main = main.dropna(subset=["cnpj", "year_month", "indicator_value"])

    # WARNING: unweighted mean across sets is a proxy, not an official distributor aggregate.
    proxy_long = (main.groupby(["cnpj", "year_month", "indicator"], as_index=False)
                  .agg(unweighted_mean=("indicator_value", "mean"),
                       set_count=("IdeConjUndConsumidoras", "nunique")))
    proxy = proxy_long.pivot(index=["cnpj", "year_month"], columns="indicator",
                             values="unweighted_mean").reset_index()
    proxy.columns.name = None
    proxy = proxy.rename(columns={"DEC": "DEC_unweighted_mean_proxy",
                                  "FEC": "FEC_unweighted_mean_proxy"})
    set_counts = proxy_long.pivot(index=["cnpj", "year_month"], columns="indicator",
                                  values="set_count").reset_index()
    set_counts.columns.name = None
    set_counts = set_counts.rename(columns={"DEC": "DEC_set_count", "FEC": "FEC_set_count"})
    proxy = proxy.merge(set_counts, on=["cnpj", "year_month"], how="left")

    # Aggregate manifestations by distributor and competence month.
    manifestations["cnpj"] = clean_cnpj(manifestations["NumCPFCNPJ"])
    manifestations["year_month"] = year_month(
        manifestations["AnoCompetencia"], manifestations["MesCompetencia"])
    manifestations["code"] = pd.to_numeric(
        manifestations["CodTipoManifestacao"], errors="coerce").astype("Int64")
    manifestations["received"] = number_br(manifestations["QtdManifestacoesRecebidas"])
    manifestations["procedent"] = number_br(manifestations["QtdManifestacoesProcedentes"])
    valid_m = manifestations.dropna(subset=["cnpj", "year_month"])

    complaints = (valid_m.groupby(["cnpj", "year_month"], as_index=False)
                  .agg(total_manifestations_received=("received", "sum"),
                       total_manifestations_procedent=("procedent", "sum"),
                       source_rows=("code", "size")))
    complaints["procedent_rate"] = (
        complaints["total_manifestations_procedent"] /
        complaints["total_manifestations_received"].replace(0, pd.NA))

    # Preserve detail by manifestation code for a reviewed classification later.
    by_code = (valid_m.groupby(["cnpj", "year_month", "code"], as_index=False)
               .agg(manifestations_received=("received", "sum"),
                    manifestations_procedent=("procedent", "sum")))

    # Only matching distributor-months will have continuity values.
    analytical = complaints.merge(proxy, on=["cnpj", "year_month"], how="left",
                                   validate="one_to_one")

    complaints.to_csv(PROCESSED_DIR / "complaints_distributor_month.csv", index=False)
    by_code.to_csv(PROCESSED_DIR / "complaints_by_code_distributor_month.csv", index=False)
    proxy.to_csv(PROCESSED_DIR / "continuity_distributor_month_proxy.csv", index=False)
    analytical.to_csv(PROCESSED_DIR / "analytical_distributor_month.csv", index=False)

    report = [
        "ANEEL DATA QUALITY REPORT", "=========================",
        f"Continuity source rows: {len(continuity):,}",
        f"Manifestation source rows: {len(manifestations):,}",
        f"Consolidated DEC/FEC rows: {len(main):,}",
        f"Complaint distributor-month rows: {len(complaints):,}",
        f"Joined distributor-month rows: {len(analytical):,}",
        f"Missing CNPJ in continuity: {continuity['cnpj'].isna().sum():,}",
        f"Missing CNPJ in manifestations: {manifestations['cnpj'].isna().sum():,}",
        f"Invalid continuity month: {continuity['year_month'].isna().sum():,}",
        f"Invalid manifestation month: {manifestations['year_month'].isna().sum():,}",
        f"Missing DEC proxy after join: {analytical['DEC_unweighted_mean_proxy'].isna().sum():,}",
        f"Missing FEC proxy after join: {analytical['FEC_unweighted_mean_proxy'].isna().sum():,}",
        "",
        "WARNING: DEC/FEC values are unweighted means across consumer-unit sets.",
        "They are exploratory proxies, not official distributor-level aggregates.",
        "Verify ANEEL aggregation methodology and weighting requirements.",
        "Manifestation code classification has not yet been approved."
    ]
    (OUTPUTS_DIR / "data_quality_report.txt").write_text("\\n".join(report), encoding="utf-8")
    print("Preparation complete. Review outputs/data_quality_report.txt")


if __name__ == "__main__":
    main()
