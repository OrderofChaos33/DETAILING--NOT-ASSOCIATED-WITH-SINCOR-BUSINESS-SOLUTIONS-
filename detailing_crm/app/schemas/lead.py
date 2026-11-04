from pydantic import BaseModel, Field


class InboundLeadPayload(BaseModel):
    phone: str = Field(..., description="Client phone number")
    source: str = Field(..., description="Lead source channel")
    message: str | None = Field(None, description="Inbound text or form query")
    name: str | None = Field(None, description="Client name if provided")
