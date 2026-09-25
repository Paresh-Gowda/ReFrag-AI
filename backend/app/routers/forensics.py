from typing import List, Optional
from fastapi import APIRouter, Depends, Form, UploadFile, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.forensic import UploadResponse, CaseDetailResponse, ArtifactSummary
from app.services.forensic_service import ForensicService

router = APIRouter(prefix="/api/forensics", tags=["Forensic Ingestion"])

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_forensic_dataset(
    files: List[UploadFile],
    relative_paths: Optional[List[str]] = Form(None),
    case_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingest forensic artifacts (files or directory structures).
    Calculates SHA-256, extracts file signatures, and persists exact bytes into database.
    """
    return await ForensicService.process_upload(
        db=db,
        files=files,
        relative_paths=relative_paths,
        case_name=case_name
    )

@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
def get_case_details(case_id: str, db: Session = Depends(get_db)):
    """
    Retrieve forensic case summary and artifact metadata list.
    """
    return ForensicService.get_case_detail(db=db, case_id=case_id)

@router.get("/artifacts/{artifact_id}", response_model=ArtifactSummary)
def get_artifact_details(artifact_id: str, db: Session = Depends(get_db)):
    """
    Retrieve metadata for a specific forensic artifact.
    """
    art = ForensicService.get_artifact(db=db, artifact_id=artifact_id)
    return ArtifactSummary(
        artifact_id=art.id,
        filename=art.original_filename,
        relative_path=art.relative_path,
        file_extension=art.file_extension,
        mime_type=art.mime_type,
        size=art.file_size,
        sha256=art.sha256_hash,
        magic_signature=art.magic_signature,
        is_duplicate=art.is_duplicate,
        created_at=art.created_at
    )

@router.get("/artifacts/{artifact_id}/download")
def download_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """
    Download/retrieve raw binary bytes of a stored artifact for integrity verification.
    """
    art = ForensicService.get_artifact(db=db, artifact_id=artifact_id)
    return Response(
        content=art.content,
        media_type=art.mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{art.original_filename}"',
            "X-SHA256-Hash": art.sha256_hash
        }
    )
