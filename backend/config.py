from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT_DIR / 'code' / 'runs' / 'detect' / 'train2' / 'weights' / 'best.pt'
DEFAULT_SOURCE_PATH = ROOT_DIR / 'input_images'
DEFAULT_OUTPUT_DIR = ROOT_DIR / 'output_images'


@dataclass(frozen=True)
class Settings:
    supabase_url: str | None
    supabase_service_role_key: str | None
    supabase_bucket: str
    runs_table: str
    results_table: str
    model_path: Path
    source_path: Path
    output_dir: Path
    run_name: str
    confidence: float
    dry_run: bool


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def load_settings(
    *,
    model_path: str | None = None,
    source_path: str | None = None,
    output_dir: str | None = None,
    run_name: str | None = None,
    confidence: float | None = None,
    dry_run: bool | None = None,
) -> Settings:
    return Settings(
        supabase_url=os.getenv('SUPABASE_URL') or None,
        supabase_service_role_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY') or None,
        supabase_bucket=os.getenv('SUPABASE_BUCKET', 'annotated-outputs'),
        runs_table=os.getenv('SUPABASE_RUNS_TABLE', 'inference_runs'),
        results_table=os.getenv('SUPABASE_RESULTS_TABLE', 'inference_images'),
        model_path=Path(model_path or os.getenv('MODEL_PATH') or DEFAULT_MODEL_PATH),
        source_path=Path(source_path or os.getenv('SOURCE_PATH') or DEFAULT_SOURCE_PATH),
        output_dir=Path(output_dir or os.getenv('OUTPUT_DIR') or DEFAULT_OUTPUT_DIR),
        run_name=run_name or os.getenv('RUN_NAME') or 'local-run',
        confidence=confidence if confidence is not None else float(os.getenv('DEFAULT_CONFIDENCE', '0.25')),
        dry_run=dry_run if dry_run is not None else _to_bool(os.getenv('DRY_RUN'), False),
    )
