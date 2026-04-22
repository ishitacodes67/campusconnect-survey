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
            raise ValueError("Select at least one option")
        return [item.strip() for item in v if item.strip()]

    @field_validator("biggest_problem")
    @classmethod
    def non_empty_text(cls, v):
        if not v or not v.strip():
            raise ValueError("biggest_problem cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def sanitize(self):
        for f in ["role","year","dept","missed","ai_reco","notif_freq","privacy"]:
            val = getattr(self, f)
            if val: setattr(self, f, val.strip()[:500])
        for f in ["biggest_problem","wishlist","other"]:
            val = getattr(self, f)
            if val: setattr(self, f, val.strip()[:2000])
        return self

class DashboardLogin(BaseModel):
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
