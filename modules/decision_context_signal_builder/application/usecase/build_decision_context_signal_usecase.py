from modules.observations.application.port.observation_repository_port import ObservationRepositoryPort


class BuildDecisionContextSignalUseCase:

    def __init__(
        self,
        observation_repo: ObservationRepositoryPort,
    ):
        self.observation_repo = observation_repo

    def execute_with_candidates(self, candidates: list[int]):
        pass
