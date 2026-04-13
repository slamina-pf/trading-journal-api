from pydantic import BaseModel, field_validator
from typing import Optional


class StrategyStepSchema(BaseModel):
    position: int
    title:    Optional[str] = None
    content:  str

    @field_validator("position")
    @classmethod
    def position_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("position must be 1 or greater")
        return v

    @field_validator("title")
    @classmethod
    def title_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) > 100:
            raise ValueError("title cannot exceed 100 characters")
        return v.strip() if v else v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("content cannot be empty")
        return v


class CreateStrategySchema(BaseModel):
    name:  str
    steps: list[StrategyStepSchema]

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        if len(v) > 100:
            raise ValueError("name cannot exceed 100 characters")
        return v

    @field_validator("steps")
    @classmethod
    def steps_not_empty(cls, v: list[StrategyStepSchema]) -> list[StrategyStepSchema]:
        if not v:
            raise ValueError("a strategy must have at least one step")
        positions = [s.position for s in v]
        if len(positions) != len(set(positions)):
            raise ValueError("step positions must be unique")
        return v
