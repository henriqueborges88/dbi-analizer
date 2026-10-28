#requires -Version 7.0
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')]
    [string]$Repository
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$taskCmdlet = $PSCmdlet
$apiRoot = "repos/$Repository"

function Invoke-RepositoryApi {
    param(
        [string]$Method = 'GET',
        [Parameter(Mandatory)][string]$Endpoint,
        [hashtable]$Body
    )

    if ($Method -ne 'GET' -and -not $taskCmdlet.ShouldProcess($Endpoint, $Method)) {
        return
    }

    $taskArguments = @('api', '--method', $Method, $Endpoint,
        '-H', 'Accept: application/vnd.github+json',
        '-H', 'X-GitHub-Api-Version: 2022-11-28')
    if ($null -ne $Body) {
        $taskJson = ConvertTo-Json -InputObject $Body -Depth 12 -Compress
        $taskResponse = $taskJson | & gh @taskArguments --input -
    } else {
        $taskResponse = & gh @taskArguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub API failed: $Method $Endpoint. $($taskResponse -join ' ')"
    }
    if ($taskResponse) {
        return ($taskResponse -join "`n" | ConvertFrom-Json -AsHashtable)
    }
}

function Assert-Control {
    param([bool]$Condition, [string]$Name)
    if (-not $Condition) { throw "Verification failed: $Name" }
    Write-Host "Verified: $Name"
}

Get-Command gh -ErrorAction Stop | Out-Null
$repositoryInfo = Invoke-RepositoryApi -Endpoint $apiRoot
if (-not $repositoryInfo.permissions.admin) {
    throw 'Repository administration permission is required.'
}
if ($repositoryInfo.default_branch -ne 'main') {
    throw 'Expected main to be the default branch; inspect the repository before applying this policy.'
}

$actions = Invoke-RepositoryApi -Endpoint "$apiRoot/actions/permissions"
Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/actions/permissions" -Body @{
    enabled = $true
    allowed_actions = $actions.allowed_actions
    sha_pinning_required = $true
} | Out-Null
Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/actions/permissions/workflow" -Body @{
    default_workflow_permissions = 'read'
    can_approve_pull_request_reviews = $false
} | Out-Null
Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/vulnerability-alerts" | Out-Null
Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/automated-security-fixes" | Out-Null

if (-not $WhatIfPreference) {
    $actions = Invoke-RepositoryApi -Endpoint "$apiRoot/actions/permissions"
    Assert-Control ($actions.enabled -and $actions.sha_pinning_required) 'Actions require full commit SHAs'
    $workflow = Invoke-RepositoryApi -Endpoint "$apiRoot/actions/permissions/workflow"
    Assert-Control ($workflow.default_workflow_permissions -eq 'read' -and
        -not $workflow.can_approve_pull_request_reviews) 'Read-only default workflow token; PR approval disabled'
    Invoke-RepositoryApi -Endpoint "$apiRoot/vulnerability-alerts" | Out-Null
    Write-Host 'Verified: Dependabot alerts enabled'
    $updates = Invoke-RepositoryApi -Endpoint "$apiRoot/automated-security-fixes"
    Assert-Control ($updates.enabled -and -not $updates.paused) 'Dependabot security updates enabled'
}

if ($repositoryInfo.visibility -ne 'public') {
    Write-Warning 'Repository is private. Public-only controls remain pending: main branch protection, external workflow approval, secret scanning, push protection, private vulnerability reporting, and CodeQL result uploads. Visibility was not changed. Rerun after publication and after CODEOWNERS is merged into main.'
    return
}

# CODEOWNERS must exist on the base branch before the review requirement is useful.
$codeOwners = Invoke-RepositoryApi -Endpoint "$apiRoot/contents/.github/CODEOWNERS?ref=main"
$codeOwnersText = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($codeOwners.content))
$ownerRules = @($codeOwnersText -split '\r?\n' | Where-Object { $_ -match '\S' -and $_ -notmatch '^\s*#' })
if ($ownerRules.Count -ne 1 -or $ownerRules[0].Trim() -ne '* @henriqueborges88') {
    throw 'Merge the expected CODEOWNERS (* @henriqueborges88) into main before applying public settings.'
}

Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/actions/permissions/fork-pr-contributor-approval" -Body @{
    approval_policy = 'all_external_contributors'
} | Out-Null
Invoke-RepositoryApi -Method PATCH -Endpoint $apiRoot -Body @{
    security_and_analysis = @{
        secret_scanning = @{ status = 'enabled' }
        secret_scanning_push_protection = @{ status = 'enabled' }
    }
} | Out-Null
Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/private-vulnerability-reporting" | Out-Null

# Administrators may bypass branch protection; contributors require reviewed PRs.
$reviewRequirements = @{
    dismiss_stale_reviews = $true
    require_code_owner_reviews = $true
    required_approving_review_count = 1
}
# GitHub rejects actor restrictions, even empty ones, on personal repositories.
if ($repositoryInfo.owner.type -eq 'Organization') {
    $reviewRequirements.bypass_pull_request_allowances = @{ users = @(); teams = @(); apps = @() }
}
Invoke-RepositoryApi -Method PUT -Endpoint "$apiRoot/branches/main/protection" -Body @{
    required_status_checks = $null
    enforce_admins = $false
    required_pull_request_reviews = $reviewRequirements
    restrictions = $null
    required_conversation_resolution = $true
    allow_force_pushes = $false
    allow_deletions = $false
} | Out-Null

if (-not $WhatIfPreference) {
    $approval = Invoke-RepositoryApi -Endpoint "$apiRoot/actions/permissions/fork-pr-contributor-approval"
    Assert-Control ($approval.approval_policy -eq 'all_external_contributors') 'All external contributors require workflow approval'
    $security = (Invoke-RepositoryApi -Endpoint $apiRoot).security_and_analysis
    Assert-Control ($security.secret_scanning.status -eq 'enabled') 'Secret scanning enabled'
    Assert-Control ($security.secret_scanning_push_protection.status -eq 'enabled') 'Secret push protection enabled'
    $reporting = Invoke-RepositoryApi -Endpoint "$apiRoot/private-vulnerability-reporting"
    Assert-Control $reporting.enabled 'Private vulnerability reporting enabled'
    $protection = Invoke-RepositoryApi -Endpoint "$apiRoot/branches/main/protection"
    $reviews = $protection.required_pull_request_reviews
    Assert-Control ($reviews.required_approving_review_count -ge 1 -and
        $reviews.require_code_owner_reviews -and $reviews.dismiss_stale_reviews) 'Required code owner review and stale approval dismissal'
    Assert-Control (-not $protection.enforce_admins.enabled) 'Administrators are exempt from branch protection'
    Assert-Control $protection.required_conversation_resolution.enabled 'Review conversations must be resolved'
    Assert-Control (-not $protection.allow_force_pushes.enabled -and
        -not $protection.allow_deletions.enabled) 'Force pushes and main deletion blocked'
    $hasBypasses = $false
    if ($reviews.ContainsKey('bypass_pull_request_allowances')) {
        foreach ($actors in $reviews.bypass_pull_request_allowances.Values) {
            if (@($actors).Count -gt 0) { $hasBypasses = $true }
        }
    }
    Assert-Control (-not $hasBypasses) 'No PR bypass allowances'
}
