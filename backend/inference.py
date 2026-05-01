from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ultralytics import YOLO


@dataclass(frozen=True)
class PredictionSummary:
    original_path: str
    annotated_path: str
    box_count: int
    max_confidence: float | None
    width: int | None
    height: int | None


class InferenceRunner:
    def __init__(self, model_path: Path, output_dir: Path) -> None:
        self.model_path = model_path
        self.output_dir = output_dir
        self.model = YOLO(str(model_path))

    def run(self, source_path: Path, run_name: str, confidence: float) -> tuple[Path, list[PredictionSummary]]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        results = self.model.predict(
            source=str(source_path),
            conf=confidence,
            save=True,
            project=str(self.output_dir),
            name=run_name,
            exist_ok=True,
            verbose=False,
        )

        if not results:
            run_dir = self.output_dir / run_name
            run_dir.mkdir(parents=True, exist_ok=True)
            return run_dir, []

        run_dir = Path(results[0].save_dir)
        summaries: list[PredictionSummary] = []

        for result in results:
            original_path = Path(result.path)
            annotated_path = run_dir / original_path.name
            boxes = getattr(result, "boxes", None)
            box_count = len(boxes) if boxes is not None else 0
            confidences = [float(box.conf[0]) for box in boxes] if boxes is not None and len(boxes) else []
            max_confidence = max(confidences) if confidences else None
            shape = getattr(result, "orig_shape", None)
            height = int(shape[0]) if shape else None
            width = int(shape[1]) if shape else None
            summaries.append(
                PredictionSummary(
                    original_path=str(original_path),
                    annotated_path=str(annotated_path),
                    box_count=box_count,
                    max_confidence=max_confidence,
                    width=width,
                    height=height,
                )
            )

        return run_dir, summaries
