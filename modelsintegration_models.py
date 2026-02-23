"""
Data models for the Dynamic Integration Nexus.
Using Python dataclasses for type safety and validation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json

@dataclass
class AIModule:
    """Represents an AI module in the ecosystem."""
    module_id: str
    name: str
    version: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "active"  # active, inactive, degraded
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Firestore-compatible dictionary."""
        data = self.__dict__.copy()
        data['created_at'] = self.created_at.isoformat()
        if self.last_heartbeat:
            data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIModule':
        """Create from Firestore dictionary."""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_heartbeat'):
            data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return cls(**data)

@dataclass
class IntegrationPattern:
    """Represents discovered integration patterns between modules."""
    pattern_id: str
    source_modules: List[str]
    target_modules: List[str]
    average_latency: float
    success_rate: float