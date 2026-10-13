"""Service for file storage using Supabase Storage."""

from typing import Optional, BinaryIO
from uuid import UUID, uuid4
import io
from supabase import Client
from app.core.config import settings
from app.core.exceptions import ValidationError


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
            # Upload file
            response = self.client.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            
            # Persist the storage key; public URLs are derived when needed and
            # should not be parsed back into a key during deletion.
            return file_path
        except Exception as e:
            error_msg = str(e)
            print(f"Storage upload error: {error_msg}")
            raise ValidationError(f"Failed to upload file: {error_msg}")

    async def delete_resume(self, file_path: str) -> None:
        """Delete resume file from storage."""
        try:
            self.client.storage.from_(self.bucket).remove([file_path])
        except Exception as e:
            raise ValidationError(f"Failed to delete file: {str(e)}")

    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file."""
        return self.client.storage.from_(self.bucket).get_public_url(file_path)


# Singleton instance
storage_service = StorageService()
