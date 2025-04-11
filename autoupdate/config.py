from pathlib import Path

from models import CoprProject

username = "lihaohong"
project_root = Path("..")

all_projects = [
    CoprProject("chezmoi", 232604),
    CoprProject("yazi", 370571),
    CoprProject("scc", 376740),
    CoprProject("bazel", 15227, test_build_locally=False),
    CoprProject("bazel7", 15227, copr_repo="bazel", version_filter=lambda v: v.startswith("7"), test_build_locally=False),
    CoprProject("codeberg-cli", 377554),
    CoprProject("forgejo-cli", 377539),
    CoprProject("resvg", 377646),
]
