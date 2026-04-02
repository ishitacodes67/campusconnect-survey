"""
Pydantic models — strict validation so no bad data ever hits the database.
"""

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class SurveyResponse(BaseModel):
    role:            str
    year:            str
    dept:            str
    discover:        list[str]
    missed:          str
    comm_score:      int
    interests:       list[str]
    ai_reco:         str
    notif:           list[str]
    notif_freq:      str
    features:        list[str]
    privacy:         str
    likely_score:    int
    biggest_problem: str
    wishlist:        Optional[str] = ""
    other:           Optional[str] = ""

    @field_validator("role")
    @classmethod
    def valid_role(cls, v):
        allowed = {"Student", "Faculty"}
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v

    @field_validator("comm_score", "likely_score")
    @classmethod
    def valid_score(cls, v):
        if not (1 <= v <= 5):
            raise ValueError("Score must be between 1 and 5")
        return v

    @field_validator("discover", "notif", "features", "interests")
    @classmethod
    def non_empty_list(cls, v):
        if not v:
            raise ValueError("This field requires at least one selection")
        return [item.strip() for item in v if item.strip()]

    @field_validator("biggest_problem")
    @classmethod
    def non_empty_text(cls, v):
        if not v or not v.strip():
            raise ValueError("biggest_problem cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def sanitize_strings(self):
        for field in ["role", "year", "dept", "missed", "ai_reco", "notif_freq", "privacy"]:
            val = getattr(self, field)
            if val:
                setattr(self, field, val.strip()[:500])
        for field in ["biggest_problem", "wishlist", "other"]:
            val = getattr(self, field)
            if val:
                setattr(self, field, val.strip()[:2000])
        return self


class DashboardLogin(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
