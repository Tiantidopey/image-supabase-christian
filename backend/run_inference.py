from __future__ import annotations

from datetime import datetime, timezone
import argparse

from config import load_settings
from inference import InferenceRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run YOLO inference on a folder and save outputs locally')
    parser.add_argument('--source', help='Image file or folder to process')
    parser.add_argument('--model', help='Path to the trained YOLO weights')
    parser.add_argument('--output-dir', help='Directory for annotated outputs')
    parser.add_argument('--run-name', help='Name for this inference run')
    parser.add_argument('--confidence', type=float, help='Confidence threshold')
    parser.add_argument('--nms-iou', type=float, help='IoU threshold for NMS suppression')
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
        nms_iou=args.nms_iou,
    )

    runner = InferenceRunner(settings.model_path, settings.output_dir)
    run_dir, summaries = runner.run(
        settings.source_path,
        settings.run_name,
        settings.confidence,
        settings.nms_iou,
    )

    print(f'Results saved to {run_dir}')
    print(f'Images processed: {len(summaries)}')


if __name__ == '__main__':
    main()
