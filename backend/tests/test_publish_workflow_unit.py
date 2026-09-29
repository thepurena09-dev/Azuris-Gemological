from types import SimpleNamespace
from unittest.mock import AsyncMock
from pathlib import Path

import pymupdf
import pytest

import services.issuance as issuance
from services.certificate_pdf import build_card_pdf, build_certificate_pdf


def complete_gemstone(certificate_id=None):
    return SimpleNamespace(
        uuid="gem-1", gem_code="EMD", name_en="Emerald",
        gemstone_type="Natural Beryl", weight_carat=3.25,
        color="Vivid Green", transparency="Transparent", clarity="Eye Clean", cut="Emerald Cut",
        shape="Rectangular", dimensions_mm="9 x 7 x 4 mm",
        origin="Colombia", examiner="AGR Gemologist", media_ids=["photo-1"], certificate_id=certificate_id,
    )


@pytest.mark.asyncio
async def test_publish_creates_once_then_reissues_without_new_number(monkeypatch):
    gem = complete_gemstone()
    updates = []

    class GemRepo:
        def __init__(self, _db):
            pass

        async def get_by_uuid(self, _uuid):
            return gem

        async def update_one(self, *args):
            updates.append(args)

    issue = AsyncMock(return_value={
        "certificate_uuid": "cert-1", "certificate_number": "AGR-EMD-000001-26"
    })
    reissue = AsyncMock(return_value={
        "certificate_uuid": "cert-2", "certificate_number": "AGR-EMD-000001-26", "version": 2
    })
    monkeypatch.setattr(issuance, "GemstoneRepository", GemRepo)
    monkeypatch.setattr(issuance, "issue_certificate", issue)
    monkeypatch.setattr(issuance, "reissue_certificate", reissue)
    monkeypatch.setattr(issuance, "write_audit_log", AsyncMock())
    admin = SimpleNamespace(uuid="admin-1", role="administrator")

    first = await issuance.publish_gemstone(None, admin, gem.uuid, {})
    assert first["status"] == "published"
    issue.assert_awaited_once()
    reissue.assert_not_awaited()

    gem.certificate_id = "cert-1"
    second = await issuance.publish_gemstone(None, admin, gem.uuid, {})
    reissue.assert_awaited_once_with(None, admin, "cert-1", {})
    assert second["certificate_number"] == first["certificate_number"]
    assert any(update[1]["status"] == "published" for update in updates)


@pytest.mark.asyncio
async def test_publish_rejects_incomplete_gemstone(monkeypatch):
    gem = complete_gemstone()
    gem.media_ids = []

    class GemRepo:
        def __init__(self, _db):
            pass

        async def get_by_uuid(self, _uuid):
            return gem

    monkeypatch.setattr(issuance, "GemstoneRepository", GemRepo)
    with pytest.raises(Exception) as error:
        await issuance.publish_gemstone(None, SimpleNamespace(uuid="a", role="administrator"), gem.uuid, {})
    assert error.value.status_code == 422
    assert "examination photo" in error.value.detail


def test_certificate_and_two_sided_card_render_with_photo_and_signature():
    assets = Path(__file__).parents[1] / "assets"
    payload = {
        "certificate_number": "AGR-EMD-000001-26",
        "issued_at": "2026-09-29",
        "gemstone_snapshot": {
            "name_en": "Emerald", "species": "Natural Beryl", "carat": 3.25,
            "dimensions": "9 x 7 x 4 mm", "shape": "Rectangular",
            "cut": "Emerald Cut", "color": "Vivid Green",
            "transparency": "Transparent", "clarity": "Eye Clean",
            "origin": "Colombia", "examiner": "AGR Gemologist",
        },
        "legality_snapshot": {
            "certificate_name": "Laboratory Accreditation",
            "signatory_name": "A. Rahmani", "signatory_position": "Chief Gemologist",
        },
    }
    photo = (assets / "sample-gemstone.png").read_bytes()
    signature = (assets / "sample-signature.png").read_bytes()
    certificate = pymupdf.open(stream=build_certificate_pdf(payload, photo, signature), filetype="pdf")
    card = pymupdf.open(
        stream=build_card_pdf(
            payload,
            photo,
            "https://example.test/verify",
            signature_bytes=signature,
        ),
        filetype="pdf",
    )
    try:
        assert len(certificate) == 4
        assert len(card) == 2
        assert certificate[2].get_images(), "gemstone presentation page must contain the uploaded photo"
        assert card[0].get_images(), "card front must contain the gemstone photo and QR code"
        assert len(card[1].get_images(full=True)) >= 2, (
            "card back must contain both the AGR brand and authorised signature images"
        )
    finally:
        certificate.close()
        card.close()
