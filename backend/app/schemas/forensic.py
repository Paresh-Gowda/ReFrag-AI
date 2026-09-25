from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ArtifactSummary(BaseModel):
    artifact_id: str
    filename: str
    relative_path: str
    file_extension: Optional[str] = None
    mime_type: Optional[str] = None
    size: int
    sha256: str
    magic_signature: Optional[str] = None
    is_duplicate: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    case_id: str
    case_name: str
    files_uploaded: int
    total_size: int
    status: str
    created_at: datetime
    artifacts: List[ArtifactSummary]

    model_config = ConfigDict(from_attributes=True)

class CaseDetailResponse(BaseModel):
    case_id: str
    case_name: str
    status: str
    created_at: datetime
    total_files: int
    total_size: int
    artifacts: List[ArtifactSummary]

    model_config = ConfigDict(from_attributes=True)
