# prepare-and-open-pr.ps1
# Usage:
#   1. Make sure you have forked or let the script fork for you.
#   2. Run:  .\prepare-and-open-pr.ps1 -GithubToken "ghp_xxx" -GithubUsername "yourusername"
#
# This script will:
# - Add the fork as remote (using token for auth)
# - Push the current branch
# - Create the Pull Request via GitHub API

param(
    [Parameter(Mandatory=$true)]
    [string]$GithubToken,

    [Parameter(Mandatory=$true)]
    [string]$GithubUsername,

    [string]$UpstreamOwner = "MPDL",
    [string]$UpstreamRepo = "KEEPER",
    [string]$Branch = "feature/self-service-email-migration",
    [string]$BaseBranch = "master"   # Change to "main" if the repo uses main
)

$ErrorActionPreference = "Stop"

$authHeader = @{
    Authorization = "token $GithubToken"
    "User-Agent"  = "keeper-migration-pr-script"
    Accept        = "application/vnd.github+json"
}

Write-Host "=== Preparing PR for $UpstreamOwner/$UpstreamRepo ==="

# 1. Ensure we are on the right branch
git checkout $Branch

# 2. Create fork if it doesn't exist yet (idempotent-ish)
Write-Host "Checking/creating fork under $GithubUsername ..."
try {
    $forkResp = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$UpstreamOwner/$UpstreamRepo/forks" -Headers $authHeader -Body '{}' -ContentType "application/json"
    Write-Host "Fork created or already existed."
} catch {
    if ($_.Exception.Response.StatusCode -eq 202 -or $_.Exception.Response.StatusCode -eq 422) {
        Write-Host "Fork request accepted (or already exists)."
    } else {
        Write-Host "Fork check: $($_.Exception.Message)"
    }
}

$forkRemote = "https://x-access-token:${GithubToken}@github.com/${GithubUsername}/${UpstreamRepo}.git"

# 3. Add or update the fork remote
if ((git remote) -contains "fork") {
    git remote set-url fork $forkRemote
} else {
    git remote add fork $forkRemote
}

Write-Host "Pushing branch $Branch to fork..."
git push -u fork $Branch --force-with-lease

# 4. Create the Pull Request
$prTitle = "feat: Self-service email account migration"
$prBody = Get-Content -Raw proposed-pr/PR_DESCRIPTION.md

$prPayload = @{
    title = $prTitle
    head  = "${GithubUsername}:${Branch}"
    base  = $BaseBranch
    body  = $prBody
} | ConvertTo-Json -Depth 5

Write-Host "Creating Pull Request..."
try {
    $pr = Invoke-RestMethod -Method Post `
        -Uri "https://api.github.com/repos/$UpstreamOwner/$UpstreamRepo/pulls" `
        -Headers $authHeader `
        -Body $prPayload `
        -ContentType "application/json"

    Write-Host "✅ PR created successfully!"
    Write-Host "URL: $($pr.html_url)"
} catch {
    Write-Error "Failed to create PR: $($_.Exception.Message)"
    if ($_.ErrorDetails.Message) {
        Write-Error $_.ErrorDetails.Message
    }
}
