from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field

_WEEKDAY_NAME_TO_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class RelativeDateExpression(BaseModel):

    weekday_name: Optional[str] = Field(
        None,
        description="Lowercase weekday name if the phrase refers to a specific "
        "day of the week (e.g. 'next Friday' -> 'friday'), else null.",
    )
    weeks_ahead: Optional[int] = Field(
        1,
        description="For weekday-based phrases: 0 means the soonest occurrence "
        "of that weekday (including if today happens to be that day), "
        "1 means 'next <weekday>' skipping to the following week if today "
        "already is that weekday. Most natural phrasing implies 1. "
        "Null/omit entirely if this isn't a weekday-based expression.",
    )
    days_offset: Optional[int] = Field(
        None,
        description="For phrases like 'in two weeks' or 'in 3 days', the "
        "number of calendar days from today. Null if not this kind of expression.",
    )


def resolve_relative_date(expr: RelativeDateExpression, today: date) -> date:
    if expr.days_offset is not None:
        return today + timedelta(days=expr.days_offset)

    if expr.weekday_name:
        weekday_name = expr.weekday_name.strip().lower()
        if weekday_name not in _WEEKDAY_NAME_TO_INDEX:
            raise ValueError(f"Unrecognized weekday name: {expr.weekday_name!r}")

        # weeks_ahead defaults to 1 (the documented "next <weekday>" behavior)
        # if the LLM left it null while still specifying a weekday_name —
        # this can happen since the field is Optional to tolerate explicit
        # JSON nulls from the LLM, not just omission.
        weeks_ahead = expr.weeks_ahead if expr.weeks_ahead is not None else 1

        target_weekday = _WEEKDAY_NAME_TO_INDEX[weekday_name]
        days_until = (target_weekday - today.weekday()) % 7

        # weeks_ahead=1 with days_until==0 means "today IS that weekday, but
        # the user said 'next <weekday>', so skip to next week" rather than
        # returning today's date.
        if weeks_ahead >= 1 and days_until == 0:
            days_until = 7

        days_until += max(weeks_ahead - 1, 0) * 7
        return today + timedelta(days=days_until)

    raise ValueError(
        "RelativeDateExpression has neither weekday_name nor days_offset set — "
        "nothing to resolve."
    )