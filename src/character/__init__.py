"""
角色系统模块
"""
from .attributes import Attribute, CharacterAttributes
from .realm import Realm, MajorRealm, MinorRealm
from .spirit_root import SpiritRoot, Element
from .memory import Memory, MemoryImportance, LongTermGoal, MemoryBank
from .character import Character, Position

__all__ = [
    "Attribute",
    "CharacterAttributes",
    "Realm",
    "MajorRealm",
    "MinorRealm",
    "SpiritRoot",
    "Element",
    "Memory",
    "MemoryImportance",
    "LongTermGoal",
    "MemoryBank",
    "Character",
    "Position",
]
