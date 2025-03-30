from dataclasses import dataclass
from typing import Callable


VersionFilter = Callable[[str], bool]


@dataclass
class CoprProject:
    local_name: str
    anitya_id: int
    copr_repo: str | None = None
    package_name: str | None = None
    version_filter: VersionFilter | None = None
    test_build_locally: bool = True
