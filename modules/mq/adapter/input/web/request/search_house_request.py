from pydantic import BaseModel


class SearchHouseRequest(BaseModel):
    finder_request_id: int