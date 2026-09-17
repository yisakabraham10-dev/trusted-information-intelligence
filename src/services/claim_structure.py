from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimStructure:
    subject: str | None
    predicate: str | None
    object: str | None
    constraints: tuple[str, ...]

