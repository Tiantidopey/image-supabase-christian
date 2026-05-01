from __future__ import annotations

from pathlib import Path
import mimetypes
from typing import Any

from supabase import Client, create_client


class SupabaseStore:
    def __init__(self, supabase_url: str, supabase_key: str, bucket: str, runs_table: str, results_table: str) -> None:
        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket = bucket
        self.runs_table = runs_table
        self.results_table = results_table

    def create_run(self, payload: dict[str, Any]) -> str:
        response = self.client.table(self.runs_table).insert(payload).execute()
        data = response.data or []
        if not data:
            raise RuntimeError('Supabase did not return a run row')
        return str(data[0]['id'])

    def finalize_run(self, run_id: str, payload: dict[str, Any]) -> None:
        self.client.table(self.runs_table).update(payload).eq('id', run_id).execute()

    def insert_prediction(self, payload: dict[str, Any]) -> None:
        self.client.table(self.results_table).insert(payload).execute()

    def upload_annotated_image(self, local_path: Path, object_path: str) -> str:
        bucket = self.client.storage.from_(self.bucket)
        content_type = mimetypes.guess_type(local_path.name)[0] or 'application/octet-stream'
        with local_path.open('rb') as file_handle:
            bucket.upload(
                object_path,
                file_handle,
                file_options={'content-type': content_type, 'upsert': 'true'},
            )

        public_url = bucket.get_public_url(object_path)
        if isinstance(public_url, dict):
            return str(public_url.get('publicUrl') or public_url.get('publicURL') or '')
        return str(public_url)
