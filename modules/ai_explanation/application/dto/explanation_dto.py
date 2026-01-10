from dataclasses import dataclass

@dataclass(frozen=True)
class ExplainationDto:
    explaination: str