"""Service for file storage using Supabase Storage."""

from pathlib import Path
from uuid import UUID, uuid4
from supabase import Client
from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import logger


class StorageService:
    """Service for managing file uploads to Supabase Storage."""

    def __init__(self):
        """Initialize storage service."""
        from supabase import create_client
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self.local_storage_root = Path(__file__).resolve().parents[2] / "uploads"

    async def upload_resume(
        self,
        file_content: bytes,
        filename: str,
        user_id: UUID,
        content_type: str = "application/pdf"
    ) -> str:
        """Upload resume file to Supabase Storage."""
        # Generate unique file path
        safe_filename = filename.replace("\\", "/").rsplit("/", 1)[-1]
        file_path = f"{user_id}/{uuid4().hex}_{safe_filename}"
        
        try:
            # Use the underlying HTTP client so transport exceptions are not
            # replaced by storage3's unbound-local `response` error handler.
            bucket = self.client.storage.from_(self.bucket)
            storage_client = bucket._client
            response = storage_client.request(
                "POST",
                f"/object/{bucket._get_final_path(file_path)}",
                headers={
                    **storage_client.headers,
                    "cache-control": "max-age=3600",
                    "x-upsert": "true",
                },
                files={"file": (safe_filename, file_content, content_type)},
            )
            response.raise_for_status()
            return file_path
        except Exception as error:
            # Keep the resume workflow usable when Supabase Storage is
            # temporarily unreachable. Resume extraction/scoring uses the
            # uploaded bytes and the database stores this local storage key.
            logger.warning(
                "Supabase resume upload failed; using local storage fallback",
                extra={
                    "bucket": self.bucket,
                    "filename": safe_filename,
                    "storage_error": str(error),
                },
            )
            try:
                return await self._store_locally(file_content, file_path)
            except OSError as local_error:
                raise ValidationError(
                    "Resume storage is unavailable. Verify the Supabase Storage "
                    "connection or local upload folder permissions."
                ) from local_error

    async def _store_locally(self, file_content: bytes, file_path: str) -> str:
        """Persist a resume under the private backend uploads directory."""
        destination = (self.local_storage_root / file_path).resolve()
        if not destination.is_relative_to(self.local_storage_root.resolve()):
            raise OSError("Invalid local resume path")

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file_content)
        return f"local://{file_path}"

    async def delete_resume(self, file_path: str) -> None:
        """Delete resume file from storage."""
        try:
            if file_path.startswith("local://"):
                local_key = file_path.removeprefix("local://")
                destination = (self.local_storage_root / local_key).resolve()
                if destination.is_relative_to(self.local_storage_root.resolve()):
                    destination.unlink(missing_ok=True)
                return
            self.client.storage.from_(self.bucket).remove([file_path])
        except Exception as e:
            raise ValidationError(f"Failed to delete file: {str(e)}")

    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file."""
        return self.client.storage.from_(self.bucket).get_public_url(file_path)


# Singleton instance
storage_service = StorageService()
