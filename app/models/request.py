import os
from urllib.parse import urlparse
from pydantic import BaseModel, validator
from typing import List, Optional

class DocumentQueryRequest(BaseModel):
    """Request model for URL-based document processing"""
    documents: str
    questions: List[str]
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v:
            raise ValueError('questions cannot be empty')
        if len(v) > 20:
            raise ValueError('max 20 questions allowed')
        return [q.strip() for q in v if q.strip()]
    
    @validator('documents')
    def validate_document_url(cls, v):
        allowed_extensions = ['.pdf', '.docx', '.txt']
        path = urlparse(v).path
        _, file_extension = os.path.splitext(path)
        
        if file_extension.lower() not in allowed_extensions:
            raise ValueError(f'Only {", ".join(allowed_extensions)} files are supported')
        return v

class FileUploadQueryRequest(BaseModel):
    """Request model for file upload processing — questions sent as form data"""
    questions: List[str]
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v:
            raise ValueError('questions cannot be empty')
        if len(v) > 20:
            raise ValueError('max 20 questions allowed')
        return [q.strip() for q in v if q.strip()]

class WebhookRequest(BaseModel):
    event_type: str
    payload: dict
    timestamp: str