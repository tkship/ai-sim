"""
SQLite 数据库模块
"""
import sqlite3
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager


class Database:
    """游戏数据库管理器"""

    def __init__(self, db_path: str | Path = "game.db"):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 法宝表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS treasures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    element TEXT,
                    type TEXT NOT NULL,
                    spirit_power_cost INTEGER DEFAULT 0,
                    realm_required TEXT,
                    durability INTEGER DEFAULT 100,
                    max_durability INTEGER DEFAULT 100,
                    attack_min INTEGER DEFAULT 0,
                    attack_max INTEGER DEFAULT 0,
                    defense_min INTEGER DEFAULT 0,
                    defense_max INTEGER DEFAULT 0,
                    hp_bonus INTEGER DEFAULT 0,
                    mp_bonus INTEGER DEFAULT 0,
                    spirit_bonus INTEGER DEFAULT 0,
                    speed_bonus REAL DEFAULT 0,
                    detection_bonus REAL DEFAULT 0,
                    breakthrough_bonus REAL DEFAULT 0,
                    special_effects TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_template INTEGER DEFAULT 1
                )
            """)

            # 功法表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS techniques (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    element TEXT,
                    realm_required TEXT,
                    max_level INTEGER DEFAULT 10,
                    attack_bonus REAL DEFAULT 0,
                    defense_bonus REAL DEFAULT 0,
                    cultivation_speed_bonus REAL DEFAULT 0,
                    breakthrough_bonus REAL DEFAULT 0,
                    skills TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_template INTEGER DEFAULT 1
                )
            """)

            # 角色记忆表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER DEFAULT 1,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT
                )
            """)

            # 游戏状态表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_state (
                    id INTEGER PRIMARY KEY,
                    current_year INTEGER,
                    current_month INTEGER,
                    current_day INTEGER,
                    cycle_count INTEGER DEFAULT 0,
                    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_treasures_name ON treasures(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_techniques_name ON techniques(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_character ON character_memories(character_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON character_memories(timestamp DESC)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        执行 SQL 语句

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            Cursor 对象
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict[str, Any]]:
        """
        查询单条记录

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            记录字典或 None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        """
        查询多条记录

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            记录字典列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
