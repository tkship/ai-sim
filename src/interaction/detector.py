"""探测系统模块

根据神识计算探测范围，检测并分组角色
"""
from typing import List, Tuple, Dict
from character.character import Character


class Detector:
    """探测系统类

    负责检测范围内的角色并进行分组
    """

    def __init__(self):
        """初始化探测系统"""
        pass

    def detect_nearby_characters(
        self,
        character: Character,
        all_characters: List[Character],
    ) -> List[Tuple[Character, float]]:
        """探测附近的角色

        Args:
            character: 当前角色
            all_characters: 所有角色列表

        Returns:
            附近角色列表，每个元素是 (角色, 距离) 的元组
        """
        nearby = []

        for other in all_characters:
            # 跳过自己和死亡的角色
            if other.id == character.id or not other.is_alive:
                continue

            # 计算距离
            distance = self._calculate_distance(character.position, other.position)

            # 检查是否在探测范围内
            if distance <= character.detection_range:
                nearby.append((other, distance))

        # 按距离排序
        nearby.sort(key=lambda x: x[1])

        return nearby

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """计算两点之间的距离（欧几里得距离）

        Args:
            pos1: 位置1
            pos2: 位置2

        Returns:
            距离
        """
        import math
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def group_characters(
        self,
        characters: List[Character],
    ) -> List[List[Character]]:
        """将角色分组

        根据探测范围将角色分组为互相探测到的组

        Args:
            characters: 所有角色列表

        Returns:
            分组后的角色列表
        """
        if not characters:
            return []

        # 只考虑存活的角色
        alive_chars = [c for c in characters if c.is_alive]

        if not alive_chars:
            return []

        # 使用并查集进行分组
        parent = {char.id: char.id for char in alive_chars}

        def find(char_id: str) -> str:
            """查找并查集的根节点"""
            if parent[char_id] != char_id:
                parent[char_id] = find(parent[char_id])
            return parent[char_id]

        def union(char_id1: str, char_id2: str) -> None:
            """合并两个节点的集合"""
            root1 = find(char_id1)
            root2 = find(char_id2)
            if root1 != root2:
                parent[root2] = root1

        # 检测互相能探测到的角色对
        for i, char1 in enumerate(alive_chars):
            for j in range(i + 1, len(alive_chars)):
                char2 = alive_chars[j]

                # 检查两者是否互相能探测到
                distance = self._calculate_distance(char1.position, char2.position)
                if (distance <= char1.detection_range or
                    distance <= char2.detection_range):
                    union(char1.id, char2.id)

        # 按分组收集角色
        groups = {}
        for char in alive_chars:
            root = find(char.id)
            if root not in groups:
                groups[root] = []
            groups[root].append(char)

        return list(groups.values())

    def get_group_info_for_ai(
        self,
        character: Character,
        nearby_characters: List[Tuple[Character, float]],
    ) -> List[Dict]:
        """获取附近角色信息，用于 AI 提示词

        Args:
            character: 当前角色
            nearby_characters: 附近角色列表

        Returns:
            角色信息字典列表
        """
        result = []
        for other, distance in nearby_characters:
            info = other.get_info_for_ai()
            info["distance"] = distance
            result.append(info)

        return result

    def is_in_same_group(
        self,
        char1: Character,
        char2: Character,
        max_distance: float = None,
    ) -> bool:
        """检查两个角色是否在同一组（互相能探测到）

        Args:
            char1: 角色1
            char2: 角色2
            max_distance: 最大距离，如果为 None 则使用两者的探测范围

        Returns:
            是否在同一组
        """
        distance = self._calculate_distance(char1.position, char2.position)

        if max_distance is not None:
            return distance <= max_distance
        else:
            return (distance <= char1.detection_range or
                    distance <= char2.detection_range)

    def create_interaction_pairs(
        self,
        group: List[Character],
    ) -> List[Tuple[Character, Character]]:
        """创建交互对

        对于一个分组，创建所有可能的角色对

        Args:
            group: 角色分组

        Returns:
            角色对列表
        """
        pairs = []
        for i, char1 in enumerate(group):
            for j in range(i + 1, len(group)):
                char2 = group[j]
                pairs.append((char1, char2))
        return pairs
