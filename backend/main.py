from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json

from config import load_settings
from inference import InferenceRunner
from supabase_store import SupabaseStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run YOLO inference and push annotated outputs to Supabase')
    parser.add_argument('--source', help='Image file or folder to process')
    parser.add_argument('--model', help='Path to the trained YOLO weights')
    parser.add_argument('--output-dir', help='Directory for annotated outputs')
    parser.add_argument('--run-name', help='Name for this inference run')
    parser.add_argument('--confidence', type=float, help='Confidence threshold')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase upload and only write local outputs')
    return parser.parse_args()


def _timestamp_run_name() -> str:
    return datetime.now(timezone.utc).strftime('run-%Y%m%d-%H%M%S')


def main() -> None:
    args = parse_args()
    settings = load_settings(
        model_path=args.model,
        source_path=args.source,
        output_dir=args.output_dir,
        run_name=args.run_name or _timestamp_run_name(),
        confidence=args.confidence,
        dry_run=args.dry_run,
    )

    runner = InferenceRunner(settings.model_path, settings.output_dir)
    run_dir, summaries = runner.run(settings.source_path, settings.run_name, settings.confidence)

    manifest_path = run_dir / 'manifest.json'
    manifest_path.write_text(
        json.dumps([asdict(summary) for summary in summaries], indent=2),
        encoding='utf-8',
    )

    if settings.dry_run or not settings.supabase_url or not settings.supabase_service_role_key:
        print(
            json.dumps(
                {
                    'mode': 'dry-run' if settings.dry_run else 'local-only',
                    'run_dir': str(run_dir),
                    'manifest': str(manifest_path),
                    'summaries': [asdict(summary) for summary in summaries],
                },
                indent=2,
            )
        )
        return

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
            'source_path': str(settings.source_path),
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

    print(
        json.dumps(
            {
                'mode': 'supabase',
                'run_id': run_id,
                'run_dir': str(run_dir),
                'manifest': str(manifest_path),
                'uploaded': uploaded_rows,
            },
            indent=2,
        )
    )


if __name__ == '__main__':
    main()
