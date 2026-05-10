from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import json

from config import Settings
from esp32_capture import capture_image_from_esp32
from inference import InferenceRunner
from supabase_store import SupabaseStore


def run_pipeline(settings: Settings, *, source_path: Path | None = None, capture: bool = False) -> dict[str, object]:
    selected_source = source_path or settings.source_path

    if capture:
        esp32_url = settings.esp32_url
        if not esp32_url:
            raise RuntimeError('Missing ESP32 URL. Set ESP32_URL or pass --esp32-url.')

        capture_dir = selected_source if selected_source.is_dir() else selected_source.parent
        result = capture_image_from_esp32(
            esp32_url,
            capture_dir,
            settings.capture_delay,
            settings.capture_retries,
        )
        if result is None:
            raise RuntimeError('Failed to capture image from ESP32.')

        selected_source = result.saved_path

    runner = InferenceRunner(settings.model_path, settings.output_dir)
    run_dir, summaries = runner.run(
        selected_source,
        settings.run_name,
        settings.confidence,
        settings.nms_iou,
    )

    manifest_path = run_dir / 'manifest.json'
    manifest_path.write_text(
        json.dumps([asdict(summary) for summary in summaries], indent=2),
        encoding='utf-8',
    )

    if settings.dry_run or not settings.supabase_url or not settings.supabase_service_role_key:
        return {
            'mode': 'dry-run' if settings.dry_run else 'local-only',
            'run_dir': str(run_dir),
            'manifest': str(manifest_path),
            'summaries': [asdict(summary) for summary in summaries],
        }

    store = SupabaseStore(
        settings.supabase_url,
        settings.supabase_service_role_key,
        settings.supabase_bucket,
        settings.runs_table,
        settings.results_table,
    )
    run_id = store.create_run(
        {
            'run_name': settings.run_name,
            'model_path': str(settings.model_path),
            'source_path': str(selected_source),
            'output_dir': str(run_dir),
            'confidence': settings.confidence,
            'status': 'running',
            'images_processed': len(summaries),
        }
    )

    uploaded_rows: list[dict[str, object]] = []
    for summary in summaries:
        annotated_path = Path(summary.annotated_path)
        object_name = f'{run_id}/{annotated_path.name}'
        annotated_url = store.upload_annotated_image(annotated_path, object_name)
        payload = {
            'run_id': run_id,
            'original_path': summary.original_path,
            'annotated_path': summary.annotated_path,
            'annotated_object_path': object_name,
            'annotated_url': annotated_url,
            'box_count': summary.box_count,
            'max_confidence': summary.max_confidence,
            'width': summary.width,
            'height': summary.height,
        }
        store.insert_prediction(payload)
        uploaded_rows.append(payload)

    store.finalize_run(
        run_id,
        {
            'status': 'completed',
            'images_processed': len(summaries),
            'completed_at': datetime.now(timezone.utc).isoformat(),
        },
    )

    return {
        'mode': 'supabase',
        'run_id': run_id,
        'run_dir': str(run_dir),
        'manifest': str(manifest_path),
        'uploaded': uploaded_rows,
    }
