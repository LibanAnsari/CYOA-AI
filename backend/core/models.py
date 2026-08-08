from __future__ import annotations

from typing import List
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class StoryOptionLLM(StrictBaseModel):
    text: str = Field(..., description="The text of the story option shown to the user.")

    nextNode: "StoryNodeLLM" = Field(..., description="The story node reached when this option is selected.")


class StoryNodeLLM(StrictBaseModel):
    content: str = Field(..., description="The main content of the story node.")

    isEnding: bool = Field(default=False, description="Whether this node is an ending.")

    isWinningEnding: bool = Field(default=False, description="Whether this ending is a winning ending.")

    options: List[StoryOptionLLM] = Field(default_factory=list, min_length=0, max_length=3, description="Available choices from this node.")


class StoryLLMResponse(StrictBaseModel):
    title: str = Field(..., description="The title of the story.")

    rootNode: StoryNodeLLM = Field(..., description="The root node of the story.")


StoryNodeLLM.model_rebuild()
StoryOptionLLM.model_rebuild()
