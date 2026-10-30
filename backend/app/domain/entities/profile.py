from dataclasses import dataclass


@dataclass
class Profile:
    profile_id: int | None
    user_id: int
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    title: str | None = None
    country_id: int | None = None