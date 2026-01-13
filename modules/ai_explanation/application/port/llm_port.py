from abc import ABC, abstractmethod
from typing import List


class LLMPort(ABC):
    @abstractmethod
    def generate_finder_explanation(self, items, user_message, tone) -> str:
        """임차인용 설명 생성 메서드"""
        pass

    @abstractmethod
    def generate_owner_explanation(self, request_data) -> str:
        """임대인용 설명 생성 메서드"""
        pass