"""
探测系统模块
"""
from typing import List, Set, Tuple
from dataclasses import dataclass
from ..character import Character, Position


@dataclass
class DetectionInfo:
    """探测信息"""
    target_id: str
    target_name: str
    distance: float
    realm_estimate: str
    state_hint: str = ""


class DetectionSystem:
    """探测系统"""

    @staticmethod
    def calculate_detection_range(character: Character) -> float:
        """
        计算角色的探测范围

        Args:
            character: 角色

        Returns:
            探测范围
        """
        return character.detection_range

    @staticmethod
    def detect_characters(
        observer: Character,
        all_characters: List[Character]
    ) -> List[DetectionInfo]:
        """
        探测范围内的其他角色

        Args:
            observer: 观察者
            all_characters: 所有角色列表

        Returns:
            探测到的角色信息列表
        """
        detection_range = DetectionSystem.calculate_detection_range(observer)
        detected = []

        for target in all_characters:
            if target.id == observer.id:
                continue

            distance = observer.position.distance_to(target.position)
            if distance <= detection_range:
                # 估算目标境界（基于神识差距）
                realm_estimate = DetectionSystem._estimate_realm(observer, target)
                state_hint = DetectionSystem._estimate_state(target)

                detected.append(DetectionInfo(
                    target_id=target.id,
                    target_name=target.name,
                    distance=distance,
                    realm_estimate=realm_estimate,
                    state_hint=state_hint
                ))

        # 按距离排序
        detected.sort(key=lambda x: x.distance)
        return detected

    @staticmethod
    def _estimate_realm(observer: Character, target: Character) -> str:
        """估算目标境界"""
        observer_realm = observer.realm
        target_realm = target.realm

        if target_realm > observer_realm:
            return "深不可测"
        elif target_realm == observer_realm:
            return f"{target_realm.full_name}（相当）"
        elif target_realm < observer_realm:
            return f"{target_realm.full_name}（较低）"
        return target_realm.full_name

    @staticmethod
    def _estimate_state(target: Character) -> str:
        """估算目标状态"""
        hints = []

        hp_ratio = target.attributes.hp.ratio
        if hp_ratio < 0.3:
            hints.append("伤势严重")
        elif hp_ratio < 0.6:
            hints.append("有伤在身")

        mp_ratio = target.attributes.mp.ratio
        if mp_ratio < 0.3:
            hints.append("灵力不足")

        if target.attributes.statuses:
            hints.append("状态异常")

        return "，".join(hints) if hints else "状态正常"


class InteractionGroup:
    """交互组"""

    def __init__(self, characters: List[Character]):
        self.characters = characters
        self.group_id = "_".join(sorted(c.id for c in characters))

    @property
    def size(self) -> int:
        return len(self.characters)


class InteractionDetector:
    """交互检测器"""

    @staticmethod
    def form_groups(characters: List[Character]) -> List[InteractionGroup]:
        """
        形成交互组

        Args:
            characters: 所有角色

        Returns:
            交互组列表
        """
        # 构建邻接关系
        adjacency = {c.id: set() for c in characters}
        char_map = {c.id: c for c in characters}

        for observer in characters:
            detected = DetectionSystem.detect_characters(observer, characters)
            for info in detected:
                adjacency[observer.id].add(info.target_id)
                adjacency[info.target_id].add(observer.id)

        # 使用连通分量找交互组
        visited = set()
        groups = []

        for char_id in char_map:
            if char_id not in visited:
                # BFS 找连通分量
                component = []
                queue = [char_id]
                visited.add(char_id)

                while queue:
                    current = queue.pop(0)
                    component.append(current)
                    for neighbor in adjacency[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if len(component) >= 2:
                    group_chars = [char_map[cid] for cid in component]
                    groups.append(InteractionGroup(group_chars))

        return groups

    @staticmethod
    def get_independent_characters(
        all_characters: List[Character],
        groups: List[InteractionGroup]
    ) -> List[Character]:
        """
        获取独立角色（不在任何交互组中）

        Args:
            all_characters: 所有角色
            groups: 交互组列表

        Returns:
            独立角色列表
        """
        grouped_ids = set()
        for group in groups:
            for c in group.characters:
                grouped_ids.add(c.id)

        return [c for c in all_characters if c.id not in grouped_ids]
