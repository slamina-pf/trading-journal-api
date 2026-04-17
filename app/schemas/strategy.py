from pydantic import BaseModel, field_validator
from typing import Optional


class CreateChecklistSchema(BaseModel):
    name:        str
    description: str

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        if len(v) > 100:
            raise ValueError("name cannot exceed 100 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty")
        return v


class CreateIndicatorSchema(BaseModel):
    name:        str
    description: str

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        if len(v) > 100:
            raise ValueError("name cannot exceed 100 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty")
        return v


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


class UpdateStrategySchema(BaseModel):
    name:       Optional[str]                          = None
    steps:      Optional[list[StrategyStepSchema]]     = None
    indicators: Optional[list[CreateIndicatorSchema]]  = None
    checklists: Optional[list[CreateChecklistSchema]]  = None

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        if len(v) > 100:
            raise ValueError("name cannot exceed 100 characters")
        return v

    @field_validator("steps")
    @classmethod
    def steps_valid(cls, v: Optional[list[StrategyStepSchema]]) -> Optional[list[StrategyStepSchema]]:
        if v is None:
            return v
        if not v:
            raise ValueError("a strategy must have at least one step")
        positions = [s.position for s in v]
        if len(positions) != len(set(positions)):
            raise ValueError("step positions must be unique")
        return v


class CreateStrategySchema(BaseModel):
    name:       str
    steps:      list[StrategyStepSchema]
    indicators: list[CreateIndicatorSchema] = []
    checklists: list[CreateChecklistSchema] = []

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
