from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Pagination:
    limit: int
    offset: int
