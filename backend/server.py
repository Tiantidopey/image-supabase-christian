from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import load_settings
from pipeline import run_pipeline


class CaptureRequest(BaseModel):
    esp32_url: Optional[str] = None
    confidence: Optional[float] = None
    nms_iou: Optional[float] = None


def _timestamp_run_name() -> str:
    return datetime.now(timezone.utc).strftime('run-%Y%m%d-%H%M%S')


app = FastAPI(title='ESP32 Capture Inference API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/capture-and-infer')
async def capture_and_infer(payload: CaptureRequest) -> dict[str, object]:
    settings = load_settings(
        run_name=_timestamp_run_name(),
        confidence=payload.confidence,
        esp32_url=payload.esp32_url,
        nms_iou=payload.nms_iou,
    )
    try:
        return run_pipeline(settings, capture=True)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
