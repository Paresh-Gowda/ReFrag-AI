import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_case_id():
    return f"CASE-{uuid.uuid4().hex[:8].upper()}"

def generate_uuid():
    return str(uuid.uuid4())

class ForensicCase(Base):
    __tablename__ = "forensic_cases"

    id = Column(String(50), primary_key=True, default=generate_case_id)
    case_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="ingested")
    total_files = Column(BigInteger, default=0)
    total_size = Column(BigInteger, default=0)

    artifacts = relationship("ForensicArtifact", back_populates="case", cascade="all, delete-orphan")

class ForensicArtifact(Base):
    __tablename__ = "forensic_artifacts"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    case_id = Column(String(50), ForeignKey("forensic_cases.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    relative_path = Column(Text, nullable=False)
    file_extension = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    magic_signature = Column(String(100), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    content = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("ForensicCase", back_populates="artifacts")
