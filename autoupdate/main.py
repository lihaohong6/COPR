import logging
import re
import subprocess
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import requests

from config import all_projects, username, project_root
from models import CoprProject, VersionFilter


@dataclass
class VersionInfo:
    latest: str
    all_versions: list[str]


@cache
def anitya_request_versions(project_id: int):
    return requests.get(f"https://release-monitoring.org/api/v2/versions/?project_id={project_id}").json()


def get_version_info(project_id: int, version_filter: VersionFilter | None) -> VersionInfo | None:
    try:
        response = anitya_request_versions(project_id)
        # Only return stable versions. Latest version may be a RC.
        stable_versions = response['stable_versions']
        if version_filter is None:
            return VersionInfo(stable_versions[0], stable_versions)
        good_versions = [v for v in stable_versions if version_filter(v)]
        if len(good_versions) == 0:
            logging.error(f"No suitable version found for anitya project {project_id}. Check version filter.")
            return None
        return VersionInfo(good_versions[0], good_versions)
    except Exception as e:
        logging.error(f"Anitya request error: {e}")
        return None


def get_spec_file(name: str) -> Path | None:
    spec_file = project_root / f"{name}/{name}.spec"
    if not spec_file.exists():
        logging.error(f"Cannot find spec file at {spec_file.absolute()}")
        return None
    return spec_file


@cache
def read_spec_file(name: str) -> str | None:
    file = get_spec_file(name)
    if not file:
        return None
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


VERSION_REGEX = re.compile(r"(?P<before>Version:\s*)(?P<version>\S+)\s*($|\n)")


def get_current_local_version(name: str) -> str | None:
    text = read_spec_file(name)
    version = re.search(VERSION_REGEX, text)
    if not version:
        logging.error(f"Version number not found in spec file of {name}")
        return None
    version = version.group("version")
    return version


def update_local_version(local_name: str, new_version: str) -> bool:
    text = read_spec_file(local_name)
    text, count = re.subn(VERSION_REGEX, lambda m: m.group("before") + new_version + "\n", text)
    if count == 0:
        logging.error(f"No substitution can be made for the spec file of {local_name}")
        return False
    with open(get_spec_file(local_name), "w", encoding="utf-8") as f:
        f.write(text)
    return True


@dataclass
class ProjectUpdate:
    old_version: str
    new_version: str


def update_project(project: CoprProject) -> ProjectUpdate | None:
    local_version = get_current_local_version(project.local_name)
    if local_version is None:
        return None
    version_info = get_version_info(project.anitya_id, project.version_filter)
    if version_info is None:
        return None
    if local_version not in version_info.all_versions:
        logging.error(f"Project {project.local_name} is at version {local_version} locally, "
                      f"which does not match any version on Anitya. "
                      f"Are you sure {project.anitya_id} is the correct id?")
        return None
    if version_info.latest == local_version:
        logging.debug(f"Project {project.local_name} is already at the newest version.")
        return None
    project_updated = update_local_version(project.local_name, version_info.latest)
    if not project_updated:
        return None
    return ProjectUpdate(local_version, version_info.latest)


def commit_changes(updates: list[tuple[CoprProject, ProjectUpdate]]):
    cwd = project_root
    subprocess.run(["git", "pull"], check=True, cwd=cwd)

    project_names = ", ".join(u[0].local_name for u in updates)
    logging.info(f"Projects that will be updated with git: {project_names}")

    detailed_messages = "\n".join(
        f"{u[0].local_name}: {u[1].old_version} -> {u[1].new_version}" for u in updates)
    commit_message = f"Update {project_names}\n\n{detailed_messages}"

    subprocess.run(["git", "commit", "-am", commit_message], check=True, cwd=cwd)
    subprocess.run(["git", "push"], check=True, cwd=cwd)


def try_build_locally(project: CoprProject, only_prep: bool = False) -> bool:
    cwd = project_root / project.local_name
    p = subprocess.run(["spectool", "-g", f"{project.local_name}.spec"], cwd=cwd)
    if p.returncode != 0:
        logging.error(f"spectool failed for project {project.local_name}")
        return False
    if only_prep:
        p = subprocess.run(["fedpkg", "--release", "rawhide", "prep"], cwd=cwd)
    else:
        p = subprocess.run(["fedpkg", "--release", "rawhide", "mockbuild", "--enable-network"], cwd=cwd)
    if p.returncode != 0:
        logging.error(f"fedpkg failed for project {project.local_name}")
        return False
    logging.debug(f"{project.local_name} was successfully built locally")
    return True


def copr_rebuild(project: CoprProject):
    repo_name = project.local_name if project.copr_repo is None else project.copr_repo
    repo = f"{username}/{repo_name}"
    package_name = project.local_name if project.package_name is None else project.package_name
    p = subprocess.run(["copr-cli",
                        "build-package",
                        "--nowait",
                        repo,
                        "--name", package_name,
                        "--enable-net", "on"])
    if p.returncode != 0:
        logging.error(f"Failed to call copr-cli on {project.local_name}")
        return
    logging.info(f"Rebuilt {project.local_name} on COPR")


def main():
    updates: list[tuple[CoprProject, ProjectUpdate]] = []
    for project in all_projects:
        result = update_project(project)
        if result is None:
            continue
        updates.append((project, result))
    if len(updates) == 0:
        logging.debug("No project need to be updated.")
        return
    commit_changes(updates)
    for u in updates:
        r = try_build_locally(u[0], only_prep=not u[0].test_build_locally)
        if r is False:
            continue
        copr_rebuild(u[0])


if __name__ == "__main__":
    main()
