import { createSupabaseServerClient } from '../lib/supabase';
import CaptureButton from './capture-button';

type ResultRow = {
  id: string;
  run_id: string;
  original_path: string;
  annotated_path: string;
  annotated_object_path: string;
  annotated_url: string;
  box_count: number;
  max_confidence: number | null;
  width: number | null;
  height: number | null;
  created_at: string;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

export default async function Home() {
  let results: ResultRow[] = [];
  let errorMessage = '';

  try {
    const supabase = createSupabaseServerClient();
    const { data, error } = await supabase
      .from('inference_images')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(24);

    if (error) {
      throw error;
    }

    results = (data ?? []) as ResultRow[];
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : 'Failed to load inference results.';
  }

  const latestRun = results[0]?.run_id ?? 'No run yet';
  const totalDetections = results.reduce((sum, row) => sum + row.box_count, 0);

  return (
    <main className="page">
      <section className="hero">
        <span className="eyebrow">Supabase Inference Feed</span>
        <h1>YOLO outputs streaming from the separate simulation project.</h1>
        <p>
          The Python runner processes local images, uploads annotated outputs to Supabase,
          and this dashboard renders the latest records without touching the training code.
        </p>
        <CaptureButton />
      </section>

      <dl className="stats">
        <div className="stat">
          <dt>Latest run</dt>
          <dd>{latestRun}</dd>
        </div>
        <div className="stat">
          <dt>Results loaded</dt>
          <dd>{results.length}</dd>
        </div>
        <div className="stat">
          <dt>Total detections</dt>
          <dd>{totalDetections}</dd>
        </div>
      </dl>

      {errorMessage ? <div className="error">{errorMessage}</div> : null}

      {results.length === 0 && !errorMessage ? (
        <div className="empty">
          No inference records found yet. Run the Python pipeline to populate Supabase.
        </div>
      ) : null}

      <section className="grid">
        {results.map((result) => (
          <article className="card" key={result.id}>
            <img src={result.annotated_url} alt={result.original_path} />
            <div className="card-body">
              <h2>{result.original_path}</h2>
              <div className="meta">
                <span>Run: <code>{result.run_id}</code></span>
                <span>Boxes: {result.box_count}</span>
                <span>Max confidence: {result.max_confidence ?? 'n/a'}</span>
                <span>
                  Size: {result.width ?? 'n/a'} x {result.height ?? 'n/a'}
                </span>
                <span>Uploaded: {formatDate(result.created_at)}</span>
              </div>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
