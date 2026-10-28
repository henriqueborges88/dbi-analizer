# Repository security and CODEOWNERS

This document describes the intended policy and how to apply it. Repository files and GitHub settings have separate roles; the presence of these files does not prove that server-side protections are enabled.

## Required policy for main

| Control | Required setting |
| --- | --- |
| Changes to `main` | Pull requests required for contributors; administrators may bypass protection. |
| Review | At least one approval and review from a code owner required for merges without administrator bypass. |
| Code owner | `@henriqueborges88` for every path. |
| New commits | Dismiss stale approvals when new code changes are pushed. |
| Discussions | All review conversations must be resolved before merging. |
| Administrators | Exempt from branch protection permanently (`enforce_admins: false`); no additional user, team, or app bypass allowances. |
| Force pushes | Disabled. |
| Branch deletion | Disabled. |

These restrictions are configured through GitHub branch protection, not through CODEOWNERS alone. Administrators are exempt and can merge PRs without the required approval. This exemption applies to branch protection generally, so repository maintainers should continue using PRs for routine changes. The setup script preserves the administrator exemption when rerun.

## How CODEOWNERS works

`.github/CODEOWNERS` contains:

```text
* @henriqueborges88
```

The wildcard covers the entire repository, including CODEOWNERS itself and workflow files. The owner must have write access. GitHub uses CODEOWNERS from the PR's base branch, so this file must be merged into `main` before relying on required owner review. Draft PRs do not automatically request code owner review until they are marked ready.

CODEOWNERS identifies reviewers; the **Require review from Code Owners** branch protection setting makes their approval mandatory. If more patterns are added later, the last matching pattern takes precedence. Listing multiple owners on a matching line allows any one of those owners to satisfy the owner-review requirement.

GitHub does not allow authors to approve their own PRs. With `@henriqueborges88` as the sole owner, a PR authored by that account cannot receive a valid self-approval. The account can use its administrator exemption to merge its own PR without recording an approving review. Contributor PRs still require the owner's approval when merged without administrator bypass.

## GitHub Actions

- Require approval for workflows from **all external contributors** using `all_external_contributors`, not only first-time contributors.
- Require full-length commit SHA pinning for actions through the repository Actions policy. The workflow in this repository uses verified 40-character commit SHAs, with version comments for readability.
- Keep the default `GITHUB_TOKEN` permission read-only and disable the option allowing Actions to create and approve PRs.
- Grant additional permissions only to jobs that need them. CodeQL needs `security-events: write` to upload analysis results.
- Use GitHub-hosted runners for contributions. The CodeQL workflow analyzes Python source without installing project dependencies or running the agent or samples.
- Do not introduce `pull_request_target` workflows that check out and execute untrusted PR code. Review changes to workflow files before approving an external workflow run.

External workflow approval is separate from code owner approval. A maintainer can approve an external workflow run, but that does not approve the PR for merging. SHA pinning fixes the action version; it does not establish that a workflow is safe.

## GitHub security features

| Feature | Configuration |
| --- | --- |
| Dependabot alerts | Enable repository vulnerability alerts. |
| Dependabot security updates | Enable automatic PRs for vulnerable dependencies. |
| Dependabot version updates | `.github/dependabot.yml` checks both Python requirements files and GitHub Actions weekly. |
| Code scanning | Once the repository is public, `.github/workflows/codeql.yml` analyzes Python on pushes and PRs to `main`, weekly, and on manual dispatch. The job is explicitly skipped while the repository is private. Vendored tools, samples, generated results, and virtual environments are excluded. |
| Secret scanning | Enable repository secret scanning and push protection. |
| Private vulnerability reporting | Enable private reports and follow `SECURITY.md`. |

For public repositories, the dependency graph is enabled automatically. This setup does not enable paid features. Use the committed CodeQL workflow as advanced setup; do not also enable CodeQL default setup for the same analysis. CodeQL is not configured as a required merge status check here; review its first successful runs before deciding to require that check.

## Apply the settings

Prerequisites: PowerShell 7, GitHub CLI authenticated with repository administration permissions, and the intended repository selected explicitly. This repository's GitHub name is currently `henriqueborges88/dbi-analizer`, even though the project title is `dbi-analyzer`.

1. Review and merge the repository security files into `main` as the initial setup change.
2. Run the script below. While the repository is private, it applies the supported settings and reports the public-only settings as pending.
3. When ready, make the repository public in GitHub. The script never changes repository visibility.
4. Run the same script again to apply the public-repository settings. It verifies CODEOWNERS on `main` before requiring owner approval.

```powershell
pwsh -File scripts/configure_github_security.ps1 -Repository henriqueborges88/dbi-analizer
```

Preview planned changes without applying them:

```powershell
pwsh -File scripts/configure_github_security.ps1 -Repository henriqueborges88/dbi-analizer -WhatIf
```

The script enables SHA pinning, read-only workflow tokens, Dependabot alerts and security updates. On a public repository, it also enables secret scanning, push protection, private vulnerability reporting, external workflow approval, and the `main` branch policy. It reads the resulting settings back and fails if the requested controls are not active. Its branch protection payload defines the policy above and replaces the corresponding protection configuration; review it before rerunning if you have added other branch requirements.

On the current free plan, GitHub rejects branch protection for this private repository and does not offer public-fork workflow approval until the repository is public. The script reports that limitation rather than claiming those settings are active.

## Verify in GitHub

Check **Settings > Branches**, **Settings > Actions > General**, and the repository security settings after setup. Confirm that CODEOWNERS is present on `main`, review the Security tab for scanning results, and inspect the first CodeQL run after the workflow has been merged and code scanning is available.

The initial private-repository validation successfully analyzed 27 Python and 5 HTML files, but GitHub rejected the result upload because code scanning was not enabled for the private repository. The public-only job condition prevents that unsupported upload before publication; a successful upload still needs verification after publication. Trigger **CodeQL > Run workflow** after publication if no new push or PR event occurs.

## GitHub documentation

- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Approving a pull request with required reviews](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)
- [Managing GitHub Actions settings for a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-github-actions-settings-for-a-repository)
- [GitHub Actions permissions API](https://docs.github.com/en/rest/actions/permissions)
- [Quickstart for securing your repository](https://docs.github.com/en/code-security/getting-started/quickstart-for-securing-your-repository)
