# Project Overview

This repository is a self-contained simulation project that demonstrates an end-to-end flow for YOLO inference, Supabase storage, and a Next.js dashboard. It is designed to mirror a real deployment pipeline without touching the training code.

## What this project does

1. Takes images from a local input folder.
2. Runs YOLO inference using a trained `best.pt` model.
3. Writes annotated images and a manifest locally.
4. Uploads annotated images and metadata to Supabase.
5. Displays the latest results in a Next.js web app.

## How it was created

- Built around an existing YOLO workflow (the same `yolo detect predict` flow used in Anaconda).
- Wrapped the inference step with a Python runner to collect summaries and upload to Supabase.
- Added a Next.js app to render the latest inference results.
- Added a Supabase schema for runs, image results, and storage setup.

## Structure

- `backend/` - Python runner for inference and Supabase upload.
  - `main.py` - Entry point for running inference and uploading results.
  - `inference.py` - YOLO inference wrapper and summary generation.
  - `supabase_store.py` - Supabase client and upload helpers.
  - `config.py` - Centralized settings and defaults.
- `input_images/` - Drop images here to run inference.
- `output_images/` - Annotated output images and `manifest.json` per run.
- `supabase/` - SQL schema for the hosted Supabase project.
- `web/` - Next.js app that reads Supabase and displays results.
- `code/`, `dataset/` - Training artifacts and datasets (not modified by this simulation).

## Default paths

- Input images: `simulation/input_images`
- Output images: `simulation/output_images`
- Model weights: `simulation/code/runs/detect/train2/weights/best.pt`

## Typical workflow

1. Add images to `input_images/`.
2. Activate the Python environment

   .\.venv\Scripts\Activate.ps1

   and run:

   ```bash
   python backend/main.py
   ```

3. Start the Next.js app from `web/`:

   ```bash
   npm run dev
   ```

4. Open `http://localhost:3000` to view results.

## Supabase setup summary

- Run `supabase/schema.sql` in the Supabase SQL editor.
- Set env vars in `backend/.env` and `web/.env` using your hosted Supabase URL and keys.
- The backend uses the service role key to upload images and insert rows.
- The web app uses the anon key to read the latest results.
