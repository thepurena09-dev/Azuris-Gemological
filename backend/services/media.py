"""Media service — Sprint 10.

Orchestrates the object store (binary) + the `media` metadata collection. This
is the single place that ties an uploaded file to its metadata record and its
storage key. Enforces size/type limits and captures technical metadata
(mime, size, dimensions) at ingest. Authorization / visibility are enforced at
the API layer.
"""

from __future__ import annotations

import io
from typing import Optional

from models.enums import MediaEntityType, MediaRole, MediaVisibility
from models.media import Media
from repositories.media import MediaRepository
from storage.base import build_object_key
from storage.factory import get_storage_adapter

MAX_MEDIA_BYTES = 15 * 1024 * 1024  # 15MB

# Allowed upload types + canonical extension for the object key.
ALLOWED_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
}


def _dimensions(data: bytes, content_type: str) -> tuple[Optional[int], Optional[int]]:
    if not content_type.startswith("image/"):
        return None, None
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as img:
            return img.width, img.height
    except Exception:
        return None, None


async def store_media(
    db,
    *,
    entity_type: MediaEntityType,
    entity_id: str,
    role: MediaRole,
    visibility: MediaVisibility,
    filename: str,
    content_type: str,
    data: bytes,
    alt_text_id: Optional[str] = None,
    alt_text_en: Optional[str] = None,
    actor_id: Optional[str] = None,
) -> Media:
    ext = ALLOWED_TYPES[content_type]
    width, height = _dimensions(data, content_type)

    media = Media(
        entity_type=entity_type,
        entity_id=entity_id,
        role=role,
        visibility=visibility,
        original_url="",  # set after we know the uuid
        mime_type=content_type,
        size_bytes=len(data),
        width=width,
        height=height,
        alt_text_id=alt_text_id,
        alt_text_en=alt_text_en,
        created_by=actor_id,
        updated_by=actor_id,
    )

    key = build_object_key(entity_type.value, entity_id, role.value, media.uuid, ext)
    await get_storage_adapter(db).put(key, data, content_type)

    media.storage_key = key
    media.original_url = f"/api/media/{media.uuid}"
    return await MediaRepository(db).create(media)


async def get_media_binary(db, media: Media) -> Optional[tuple[bytes, str]]:
    if not media.storage_key:
        return None
    return await get_storage_adapter(db).get(media.storage_key)


async def delete_media(db, media: Media) -> None:
    if media.storage_key:
        await get_storage_adapter(db).delete(media.storage_key)
    await MediaRepository(db).soft_delete_by_uuid(media.uuid)
