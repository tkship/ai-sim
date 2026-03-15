"""
交互系统模块
"""
from .detector import DetectionSystem, DetectionInfo, InteractionGroup, InteractionDetector
from .combat import CombatSystem, AttackResult, CombatState, CombatRoundTracker

__all__ = [
    "DetectionSystem",
    "DetectionInfo",
    "InteractionGroup",
    "InteractionDetector",
    "CombatSystem",
    "AttackResult",
    "CombatState",
    "CombatRoundTracker",
]
