# Security policy

## Reporting a vulnerability

Report vulnerabilities through [GitHub private vulnerability reporting](https://github.com/henriqueborges88/dbi-analizer/security/advisories/new) once it is enabled for the public repository. If the private reporting form is unavailable, wait for that channel to be enabled rather than posting sensitive details in a public issue.

Include the affected commit, a description of the issue, its impact, and reproduction steps using a harmless test case. Do not attach live malware, credentials, personal information, or database dumps to public issues or pull requests.

## Running the project

The agent executes input samples. Run it in a dedicated Windows lab VM. The server has no authentication and must remain restricted to the lab network. Publishing the source code does not make the server suitable for exposure to the public internet.

## Repository controls

See [Repository security and CODEOWNERS](docs/repository-security.md) for the required review policy, GitHub settings, workflow approval rules, and setup steps. Adding configuration files alone does not enable GitHub branch protection or repository security settings.
