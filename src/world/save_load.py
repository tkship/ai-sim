"""
游戏状态保存和加载模块
"""
from typing import Optional, Any
import json
from pathlib import Path
from datetime import datetime
from .database import Database
from .config import Config


class GameState:
    """游戏状态"""

    def __init__(self):
        self.current_year: int = 3842
        self.current_month: int = 3
        self.current_day: int = 7
        self.cycle_count: int = 0
        self.characters: dict[str, dict[str, Any]] = {}
        self.saved_at: Optional[datetime] = None


class SaveManager:
    """游戏存档管理器"""

    def __init__(self, db: Database, config: Config):
        self.db = db
        self.config = config

    def save_game(self, state: GameState, slot: int = 1) -> bool:
        """
        保存游戏

        Args:
            state: 游戏状态
            slot: 存档槽位

        Returns:
            是否保存成功
        """
        try:
            # 保存基本游戏状态到数据库
            self._save_world_state(state)

            # 保存角色数据
            self._save_characters(state.characters)

            # 同时保存到 JSON 文件作为备份
            self._save_to_json(state, slot)

            return True
        except Exception:
            return False

    def _save_world_state(self, state: GameState) -> None:
        """保存世界状态"""
        # 检查是否已有记录
        existing = self.db.fetch_one("SELECT id FROM game_state WHERE id = 1")

        if existing:
            sql = """
                UPDATE game_state
                SET current_year = ?, current_month = ?, current_day = ?,
                    cycle_count = ?, saved_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """
            self.db.execute(sql, (
                state.current_year,
                state.current_month,
                state.current_day,
                state.cycle_count
            ))
        else:
            sql = """
                INSERT INTO game_state
                (id, current_year, current_month, current_day, cycle_count)
                VALUES (1, ?, ?, ?, ?)
            """
            self.db.execute(sql, (
                state.current_year,
                state.current_month,
                state.current_day,
                state.cycle_count
            ))

    def _save_characters(self, characters: dict[str, dict[str, Any]]) -> None:
        """保存角色数据到数据库"""
        self.db.execute("DELETE FROM character_states")
        for character_id, payload in characters.items():
            self.db.execute(
                """
                INSERT INTO character_states (character_id, payload, saved_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (character_id, json.dumps(payload, ensure_ascii=False)),
            )

    def _save_to_json(self, state: GameState, slot: int) -> None:
        """保存到 JSON 文件"""
        save_dir = Path("saves")
        save_dir.mkdir(exist_ok=True)

        save_data = {
            "current_year": state.current_year,
            "current_month": state.current_month,
            "current_day": state.current_day,
            "cycle_count": state.cycle_count,
            "characters": state.characters,
            "saved_at": datetime.now().isoformat()
        }

        save_path = save_dir / f"save_slot_{slot}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

    def load_game(self, slot: int = 1) -> Optional[GameState]:
        """
        加载游戏

        Args:
            slot: 存档槽位

        Returns:
            游戏状态或 None
        """
        # 优先从 JSON 文件加载
        state = self._load_from_json(slot)
        if state:
            return state

        # 从数据库加载
        return self._load_from_database()

    def _load_from_json(self, slot: int) -> Optional[GameState]:
        """从 JSON 文件加载"""
        save_path = Path("saves") / f"save_slot_{slot}.json"
        if not save_path.exists():
            return None

        try:
            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            state = GameState()
            state.current_year = save_data.get("current_year", 3842)
            state.current_month = save_data.get("current_month", 3)
            state.current_day = save_data.get("current_day", 7)
            state.cycle_count = save_data.get("cycle_count", 0)
            state.characters = save_data.get("characters", {})

            if "saved_at" in save_data:
                state.saved_at = datetime.fromisoformat(save_data["saved_at"])

            return state
        except Exception:
            return None

    def _load_from_database(self) -> Optional[GameState]:
        """从数据库加载"""
        row = self.db.fetch_one("SELECT * FROM game_state WHERE id = 1")
        if not row:
            return None

        state = GameState()
        state.current_year = row.get("current_year", 3842)
        state.current_month = row.get("current_month", 3)
        state.current_day = row.get("current_day", 7)
        state.cycle_count = row.get("cycle_count", 0)
        character_rows = self.db.fetch_all("SELECT character_id, payload FROM character_states")
        for item in character_rows:
            try:
                state.characters[item["character_id"]] = json.loads(item["payload"])
            except Exception:
                continue

        return state

    def list_saves(self) -> list[dict[str, Any]]:
        """列出所有存档"""
        saves = []
        save_dir = Path("saves")

        if not save_dir.exists():
            return saves

        for save_file in save_dir.glob("save_slot_*.json"):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                slot = int(save_file.stem.replace("save_slot_", ""))
                saves.append({
                    "slot": slot,
                    "path": str(save_file),
                    "current_year": data.get("current_year"),
                    "current_month": data.get("current_month"),
                    "current_day": data.get("current_day"),
                    "saved_at": data.get("saved_at")
                })
            except Exception:
                continue

        saves.sort(key=lambda x: x["slot"])
        return saves
