from pydantic import BaseModel, model_validator
from typing import List, Optional, Literal
from datetime import datetime


class Recipe(BaseModel):
    id: int
    identifier: str


class ProcessStep(BaseModel):
    processstep: Literal[
        "slurry mixing",
        "coating & drying",
        "calendering",
        "coating, drying & calendering",
    ]
    equipment: str
    recipe: Recipe
    starttime: datetime
    endtime: datetime

    @model_validator(mode="after")
    def check_step_time(self) -> "ProcessStep":
        if self.starttime >= self.endtime:
            raise ValueError("Each process step starttime must be earlier than endtime")
        return self


class TrialBase(BaseModel):
    name: str
    description: Optional[str] = None
    starttime: Optional[datetime] = None  # Auto-calculated
    endtime: Optional[datetime] = None  # Auto-calculated
    processstep: List[ProcessStep]
    status: Literal["planned", "completed"]
    creator: str
    comment: Optional[str] = None

    @model_validator(mode="after")
    def set_trial_time(self) -> "TrialBase":
        """Automatically calculate start/end time based on process steps."""
        if not self.processstep:
            raise ValueError("Trial must contain at least one process step")

        start_times = [step.starttime for step in self.processstep]
        end_times = [step.endtime for step in self.processstep]

        calculated_start = min(start_times)
        calculated_end = max(end_times)

        # Always override to keep trial consistent with process steps
        self.starttime = calculated_start
        self.endtime = calculated_end

        if self.starttime >= self.endtime:
            raise ValueError("Trial starttime must be earlier than endtime")

        return self


class TrialCreate(TrialBase):
    pass


class TrialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    processstep: Optional[List[ProcessStep]] = None
    status: Optional[Literal["planned", "completed"]] = None
    creator: Optional[str] = None
    comment: Optional[str] = None
    starttime: Optional[datetime] = None
    endtime: Optional[datetime] = None

    @model_validator(mode="after")
    def recalc_trial_time(self) -> "TrialUpdate":
        """Recalculate trial start and end times if process steps are updated."""
        if self.processstep and len(self.processstep) > 0:
            start_times = [step.starttime for step in self.processstep]
            end_times = [step.endtime for step in self.processstep]

            self.starttime = min(start_times)
            self.endtime = max(end_times)

            if self.starttime >= self.endtime:
                raise ValueError("Trial starttime must be earlier than endtime")

        elif (
            self.starttime is not None and self.endtime is not None
        ) and self.starttime >= self.endtime:
            raise ValueError("starttime must be earlier than endtime")

        return self
