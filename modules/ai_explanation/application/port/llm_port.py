from abc import ABC, abstractmethod

class LLMPort(ABC):

    @abstractmethod
    def generate_owner_explanation(self, request_data) -> str:
        """임대인용 설명 생성 메서드"""
        pass