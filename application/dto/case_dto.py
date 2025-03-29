# Created by setup script

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class EvidenceDTO:
    id: str
    description: str
    location: str
    type: str
    found_at: datetime
    notes: Optional[str] = None


@dataclass
class SuspectDTO:
    id: str
    name: str
    description: str
    alibi: Optional[str] = None
    motive: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CaseDTO:
    title: str
    description: str
    evidence: List[EvidenceDTO]
    suspects: List[SuspectDTO]
    motives: List[str]
    notes: List[str]
    created_at: datetime
    updated_at: datetime
    status: str
    id: Optional[str] = None
