from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

CONTINUITY_FILE = RAW_DIR / "indicadores-continuidade-coletivos-2020-2029.csv"
COMPLAINTS_FILE = RAW_DIR / "manifestacoes-1-2-niveis-distribuidora-2025.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
