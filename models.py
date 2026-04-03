"""Pydantic models for the CodeReview RL environment (OpenEnv compatible)."""

from pydantic import BaseModel, Field
from typing import List, Optional


class Action(BaseModel):
    """Discrete action selecting a code fix strategy."""
    action_id: int = Field(..., ge=0, le=5, description="Fix action: 0=NOOP, 1=Semicolons, 2=Parens, 3=LoopBound, 4=PyDivision, 5=Indexing")


class Observation(BaseModel):
    """10-feature vector extracted from the code and rule engine analysis."""
    features: List[float] = Field(..., min_length=10, max_length=10, description="[semicolons, parens, boundary, floatdiv, indexing, max0, on2, score, lang_id, diff_id]")


class State(BaseModel):
    """Full internal state of the environment."""
    observation: Observation
    code: str = Field(..., description="Current code snippet")
    language: str = Field(default="JavaScript", description="Programming language")
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    score: int = Field(default=0, ge=0, le=100, description="Current rule engine score")
    done: bool = Field(default=False, description="Whether the episode is finished")
    reward: float = Field(default=0.0, description="Last step reward")


class ResetResponse(BaseModel):
    """Response from the /reset endpoint."""
    observation: Observation
    info: dict = Field(default_factory=dict)


class StepRequest(BaseModel):
    """Request body for the /step endpoint."""
    action: int = Field(..., ge=0, le=5)


class StepResponse(BaseModel):
    """Response from the /step endpoint."""
    observation: Observation
    reward: float
    terminated: bool
    truncated: bool
    info: dict = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status: str = "ok"
    environment: str = "codereview-ai"
    ai_ready: bool = False
    model: str = "gpt-4o-mini"
