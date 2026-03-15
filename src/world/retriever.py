"""
关键词检索模块
"""
from typing import Any, Optional
from .database import Database
from .repository import TreasureRepository, TechniqueRepository


class KeywordRetriever:
    """关键词检索器"""

    def __init__(self, db: Database):
        self.db = db
        self.treasure_repo = TreasureRepository(db)
        self.technique_repo = TechniqueRepository(db)

    def extract_keywords(self, text: str) -> list[str]:
        """
        从文本中提取关键词

        Args:
            text: 输入文本

        Returns:
            关键词列表
        """
        # 简单实现：按常见分隔符分割，后续可以升级为更智能的分词
        keywords = []
        separators = ["，", "。", "！", "？", "、", "；", "：", " ", ",", ".", "!", "?", ";", ":"]
        text = text.lower()

        for sep in separators:
            text = text.replace(sep, " ")

        words = text.split()
        # 过滤掉太短的词
        keywords = [w for w in words if len(w) >= 2]
        return keywords

    def retrieve_treasures(self, keywords: list[str], limit: int = 10) -> list[dict[str, Any]]:
        """
        根据关键词检索法宝

        Args:
            keywords: 关键词列表
            limit: 返回结果数量限制

        Returns:
            匹配的法宝列表
        """
        all_treasures = self.treasure_repo.get_all(only_templates=True)
        if not keywords:
            return all_treasures[:limit]

        # 简单的关键词匹配
        matched = []
        for treasure in all_treasures:
            score = self._calculate_match_score(treasure, keywords)
            if score > 0:
                treasure["match_score"] = score
                matched.append(treasure)

        # 按匹配度排序
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        return matched[:limit]

    def retrieve_techniques(self, keywords: list[str], limit: int = 10) -> list[dict[str, Any]]:
        """
        根据关键词检索功法

        Args:
            keywords: 关键词列表
            limit: 返回结果数量限制

        Returns:
            匹配的功法列表
        """
        all_techniques = self.technique_repo.get_all(only_templates=True)
        if not keywords:
            return all_techniques[:limit]

        matched = []
        for technique in all_techniques:
            score = self._calculate_match_score(technique, keywords)
            if score > 0:
                technique["match_score"] = score
                matched.append(technique)

        matched.sort(key=lambda x: x["match_score"], reverse=True)
        return matched[:limit]

    def _calculate_match_score(self, item: dict[str, Any], keywords: list[str]) -> float:
        """
        计算物品与关键词的匹配度

        Args:
            item: 物品数据
            keywords: 关键词列表

        Returns:
            匹配分数
        """
        score = 0.0
        search_text = " ".join([
            str(item.get("name", "")),
            str(item.get("element", "")),
            str(item.get("type", "")),
            str(item.get("description", ""))
        ]).lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in search_text:
                # 名称匹配权重更高
                if keyword_lower in str(item.get("name", "")).lower():
                    score += 10.0
                else:
                    score += 1.0

        return score

    def retrieve_by_item_names(self, item_names: list[str]) -> dict[str, Any]:
        """
        根据物品名称列表检索详细信息

        Args:
            item_names: 物品名称列表

        Returns:
            {
                "treasures": [...],
                "techniques": [...]
            }
        """
        result = {
            "treasures": [],
            "techniques": []
        }

        for name in item_names:
            # 查找法宝
            treasure = self.treasure_repo.get_by_name(name)
            if treasure:
                result["treasures"].append(treasure)
                continue

            # 查找功法
            technique = self.technique_repo.get_by_name(name)
            if technique:
                result["techniques"].append(technique)

        return result
