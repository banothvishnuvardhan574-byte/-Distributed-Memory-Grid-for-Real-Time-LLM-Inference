from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    cached: bool = False


class NodeInfo(BaseModel):
    node_id: int
    entries: int
    capacity: int
