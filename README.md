# Simulation Project

This folder is a separate project that simulates the end-to-end flow for YOLO inference, Supabase storage, and a Next.js dashboard.

## Flow

1. A local image folder is passed into the Python inference runner.
2. YOLO loads the trained model from `code/runs/detect/train2/weights/best.pt`.
3. Annotated prediction images are written to `simulation/backend/output/`.
4. The Python runner uploads the annotated images to Supabase Storage and inserts metadata rows.
5. The Next.js app reads Supabase and displays the latest annotated outputs.

## Structure

- `backend/` - Python inference runner and Supabase upload logic.
- `web/` - Next.js dashboard for results display.
- `supabase/` - SQL schema for runs, image results, and storage bucket setup.

## Local run

1. Create a `.env` file from the example in `backend/.env.example`.
2. Activate your Python environment, then run the local inference backend from `simulation/backend`.
3. Start the Next.js app from `simulation/web`.

## Your current manual inference command

This is the command you already run after activating `yolo11-env` in Anaconda Prompt:

```bash
yolo detect predict model=runs/detect/train2/weights/best.pt source=dataset/images save=True
```

In the separate simulation project, the Python backend is the equivalent wrapper around that same inference step. It loads the same trained weights, uses the same local image source by default, and then adds the Supabase upload step after prediction finishes.
