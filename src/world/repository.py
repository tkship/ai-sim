"""
游戏数据仓库模块 - 法宝、功法的 CRUD 操作
"""
from typing import Any, Optional
import json
from .database import Database


class TreasureRepository:
    """法宝数据仓库"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, treasure_data: dict[str, Any]) -> int:
        """创建新法宝"""
        special_effects = json.dumps(treasure_data.get("special_effects", []), ensure_ascii=False)

        sql = """
            INSERT INTO treasures (
                name, element, type, spirit_power_cost, realm_required,
                durability, max_durability, attack_min, attack_max,
                defense_min, defense_max, hp_bonus, mp_bonus, spirit_bonus,
                speed_bonus, detection_bonus, breakthrough_bonus,
                special_effects, description, is_template
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(sql, (
            treasure_data.get("name"),
            treasure_data.get("element"),
            treasure_data.get("type", "attack"),
            treasure_data.get("spirit_power_cost", 0),
            treasure_data.get("realm_required"),
            treasure_data.get("durability", 100),
            treasure_data.get("max_durability", 100),
            treasure_data.get("attack_min", 0),
            treasure_data.get("attack_max", 0),
            treasure_data.get("defense_min", 0),
            treasure_data.get("defense_max", 0),
            treasure_data.get("hp_bonus", 0),
            treasure_data.get("mp_bonus", 0),
            treasure_data.get("spirit_bonus", 0),
            treasure_data.get("speed_bonus", 0.0),
            treasure_data.get("detection_bonus", 0.0),
            treasure_data.get("breakthrough_bonus", 0.0),
            special_effects,
            treasure_data.get("description", ""),
            treasure_data.get("is_template", 1)
        ))
        return cursor.lastrowid

    def get_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """根据名称获取法宝"""
        row = self.db.fetch_one("SELECT * FROM treasures WHERE name = ?", (name,))
        if row:
            row = row.copy()
            if row.get("special_effects"):
                row["special_effects"] = json.loads(row["special_effects"])
            return row
        return None

    def get_all(self, only_templates: bool = True) -> list[dict[str, Any]]:
        """获取所有法宝"""
        sql = "SELECT * FROM treasures"
        params = ()
        if only_templates:
            sql += " WHERE is_template = 1"
        rows = self.db.fetch_all(sql, params)
        for row in rows:
            if row.get("special_effects"):
                row["special_effects"] = json.loads(row["special_effects"])
        return rows

    def update(self, treasure_id: int, updates: dict[str, Any]) -> None:
        """更新法宝"""
        if "special_effects" in updates:
            updates["special_effects"] = json.dumps(updates["special_effects"], ensure_ascii=False)

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        sql = f"UPDATE treasures SET {set_clause} WHERE id = ?"
        self.db.execute(sql, (*updates.values(), treasure_id))

    def delete(self, treasure_id: int) -> None:
        """删除法宝"""
        self.db.execute("DELETE FROM treasures WHERE id = ?", (treasure_id,))


class TechniqueRepository:
    """功法数据仓库"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, technique_data: dict[str, Any]) -> int:
        """创建新功法"""
        skills = json.dumps(technique_data.get("skills", []), ensure_ascii=False)

        sql = """
            INSERT INTO techniques (
                name, element, realm_required, max_level,
                attack_bonus, defense_bonus, cultivation_speed_bonus,
                breakthrough_bonus, skills, description, is_template
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(sql, (
            technique_data.get("name"),
            technique_data.get("element"),
            technique_data.get("realm_required"),
            technique_data.get("max_level", 10),
            technique_data.get("attack_bonus", 0.0),
            technique_data.get("defense_bonus", 0.0),
            technique_data.get("cultivation_speed_bonus", 0.0),
            technique_data.get("breakthrough_bonus", 0.0),
            skills,
            technique_data.get("description", ""),
            technique_data.get("is_template", 1)
        ))
        return cursor.lastrowid

    def get_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """根据名称获取功法"""
        row = self.db.fetch_one("SELECT * FROM techniques WHERE name = ?", (name,))
        if row:
            row = row.copy()
            if row.get("skills"):
                row["skills"] = json.loads(row["skills"])
            return row
        return None

    def get_all(self, only_templates: bool = True) -> list[dict[str, Any]]:
        """获取所有功法"""
        sql = "SELECT * FROM techniques"
        params = ()
        if only_templates:
            sql += " WHERE is_template = 1"
        rows = self.db.fetch_all(sql, params)
        for row in rows:
            if row.get("skills"):
                row["skills"] = json.loads(row["skills"])
        return rows

    def update(self, technique_id: int, updates: dict[str, Any]) -> None:
        """更新功法"""
        if "skills" in updates:
            updates["skills"] = json.dumps(updates["skills"], ensure_ascii=False)

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        sql = f"UPDATE techniques SET {set_clause} WHERE id = ?"
        self.db.execute(sql, (*updates.values(), technique_id))

    def delete(self, technique_id: int) -> None:
        """删除功法"""
        self.db.execute("DELETE FROM techniques WHERE id = ?", (technique_id,))
