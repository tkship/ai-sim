"""
游戏数据仓库模块 - 从 YAML 配置文件读写法宝、功法数据
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENT_DIR = PROJECT_ROOT / "config" / "content"


class BaseYamlRepository:
    """基于 YAML 文件的简单仓库基类"""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_items([])

    def _read_items(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []

        if not isinstance(data, list):
            raise ValueError(f"配置文件格式错误，应为列表: {self.file_path}")

        return data

    def _write_items(self, items: list[dict[str, Any]]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(items, f, allow_unicode=True, sort_keys=False)

    def _next_id(self, items: list[dict[str, Any]]) -> int:
        ids = [int(item.get("id", 0)) for item in items]
        return max(ids, default=0) + 1

    def _copy(self, item: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(item)


class TreasureRepository(BaseYamlRepository):
    """法宝数据仓库"""

    def __init__(self, db: Any = None, file_path: str | Path | None = None):
        super().__init__(file_path or DEFAULT_CONTENT_DIR / "treasures.yaml")
        self.db = db

    def create(self, treasure_data: dict[str, Any]) -> int:
        """创建新法宝"""
        items = self._read_items()
        if any(item.get("name") == treasure_data.get("name") for item in items):
            raise ValueError(f"法宝已存在: {treasure_data.get('name')}")

        item = {
            "id": self._next_id(items),
            "name": treasure_data.get("name"),
            "element": treasure_data.get("element"),
            "type": treasure_data.get("type", "attack"),
            "spirit_power_cost": treasure_data.get("spirit_power_cost", 0),
            "realm_required": treasure_data.get("realm_required"),
            "durability": treasure_data.get("durability", 100),
            "max_durability": treasure_data.get("max_durability", 100),
            "attack_min": treasure_data.get("attack_min", 0),
            "attack_max": treasure_data.get("attack_max", 0),
            "defense_min": treasure_data.get("defense_min", 0),
            "defense_max": treasure_data.get("defense_max", 0),
            "hp_bonus": treasure_data.get("hp_bonus", 0),
            "mp_bonus": treasure_data.get("mp_bonus", 0),
            "spirit_bonus": treasure_data.get("spirit_bonus", 0),
            "speed_bonus": treasure_data.get("speed_bonus", 0.0),
            "detection_bonus": treasure_data.get("detection_bonus", 0.0),
            "breakthrough_bonus": treasure_data.get("breakthrough_bonus", 0.0),
            "special_effects": treasure_data.get("special_effects", []),
            "description": treasure_data.get("description", ""),
            "is_template": treasure_data.get("is_template", 1),
        }
        items.append(item)
        self._write_items(items)
        return item["id"]

    def get_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """根据名称获取法宝"""
        for item in self._read_items():
            if item.get("name") == name:
                return self._copy(item)
        return None

    def get_all(self, only_templates: bool = True) -> list[dict[str, Any]]:
        """获取所有法宝"""
        items = self._read_items()
        if only_templates:
            items = [item for item in items if item.get("is_template", 1)]
        return [self._copy(item) for item in items]

    def update(self, treasure_id: int, updates: dict[str, Any]) -> None:
        """更新法宝"""
        items = self._read_items()
        for item in items:
            if item.get("id") == treasure_id:
                item.update(deepcopy(updates))
                self._write_items(items)
                return
        raise ValueError(f"法宝不存在: {treasure_id}")

    def delete(self, treasure_id: int) -> None:
        """删除法宝"""
        items = self._read_items()
        new_items = [item for item in items if item.get("id") != treasure_id]
        if len(new_items) == len(items):
            raise ValueError(f"法宝不存在: {treasure_id}")
        self._write_items(new_items)


class TechniqueRepository(BaseYamlRepository):
    """功法数据仓库"""

    def __init__(self, db: Any = None, file_path: str | Path | None = None):
        super().__init__(file_path or DEFAULT_CONTENT_DIR / "techniques.yaml")
        self.db = db

    def create(self, technique_data: dict[str, Any]) -> int:
        """创建新功法"""
        items = self._read_items()
        if any(item.get("name") == technique_data.get("name") for item in items):
            raise ValueError(f"功法已存在: {technique_data.get('name')}")

        item = {
            "id": self._next_id(items),
            "name": technique_data.get("name"),
            "element": technique_data.get("element"),
            "realm_required": technique_data.get("realm_required"),
            "max_level": technique_data.get("max_level", 10),
            "attack_bonus": technique_data.get("attack_bonus", 0.0),
            "defense_bonus": technique_data.get("defense_bonus", 0.0),
            "cultivation_speed_bonus": technique_data.get("cultivation_speed_bonus", 0.0),
            "breakthrough_bonus": technique_data.get("breakthrough_bonus", 0.0),
            "skills": technique_data.get("skills", []),
            "description": technique_data.get("description", ""),
            "is_template": technique_data.get("is_template", 1),
        }
        items.append(item)
        self._write_items(items)
        return item["id"]

    def get_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """根据名称获取功法"""
        for item in self._read_items():
            if item.get("name") == name:
                return self._copy(item)
        return None

    def get_all(self, only_templates: bool = True) -> list[dict[str, Any]]:
        """获取所有功法"""
        items = self._read_items()
        if only_templates:
            items = [item for item in items if item.get("is_template", 1)]
        return [self._copy(item) for item in items]

    def update(self, technique_id: int, updates: dict[str, Any]) -> None:
        """更新功法"""
        items = self._read_items()
        for item in items:
            if item.get("id") == technique_id:
                item.update(deepcopy(updates))
                self._write_items(items)
                return
        raise ValueError(f"功法不存在: {technique_id}")

    def delete(self, technique_id: int) -> None:
        """删除功法"""
        items = self._read_items()
        new_items = [item for item in items if item.get("id") != technique_id]
        if len(new_items) == len(items):
            raise ValueError(f"功法不存在: {technique_id}")
        self._write_items(new_items)
