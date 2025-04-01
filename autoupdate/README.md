# Autoupdate COPR projects

This project reads the configurations in `config.py` and checks for new versions on Anitya. If a newer version exists,
it automatically bumps the version in the spec file, commits and pushes this change, and rebuilds the project with
COPR cli.

Please be aware of the security implications of running this script unattended. A supply chain attack on upstream or
a dependency of upstream may introduce malicious code in the COPR project.
