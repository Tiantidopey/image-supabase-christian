'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

const DEFAULT_BACKEND_URL = 'http://localhost:8000';

export default function CaptureButton() {
  const router = useRouter();
  const [status, setStatus] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCapture = async () => {
    setIsLoading(true);
    setStatus('Capturing and running inference...');

    try {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? DEFAULT_BACKEND_URL;
      const response = await fetch(`${baseUrl}/capture-and-infer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const message = payload?.detail ?? 'Capture failed.';
        throw new Error(message);
      }

      setStatus('Uploaded. Refreshing feed...');
      router.refresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Capture failed.';
      setStatus(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="capture-panel">
      <button className="primary-button" onClick={handleCapture} disabled={isLoading} type="button">
        {isLoading ? 'Running...' : 'Capture + Infer'}
      </button>
      {status ? <span className="capture-status">{status}</span> : null}
    </div>
  );
}
