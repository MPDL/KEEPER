# prepare-and-open-pr.ps1
# 
# Prepares and opens the self-service email migration PR against MPDL/KEEPER.
#
# Prerequisites:
# - You must have a GitHub Personal Access Token with "repo" scope (or public_repo).
# - The token will be used only for this operation.
#
# Usage examples:
#   .\prepare-and-open-pr.ps1 -GithubToken "ghp_YourTokenHere" -GithubUsername "yourgithubname"
#   .\prepare-and-open-pr.ps1 -GithubToken $env:GITHUB_TOKEN -GithubUsername "peterfi" -BaseBranch main
#
# What it does:
# 1. Creates a fork under your account (idempotent).
# 2. Pushes the current branch (feature/self-service-email-migration) to your fork.
# 3. Opens a Pull Request from your fork to MPDL/KEEPER using the content in proposed-pr/PR_DESCRIPTION.md.

param(
    [Parameter(Mandatory=$true, HelpMessage="GitHub Personal Access Token with repo scope")]
    [string]$GithubToken,

    [Parameter(Mandatory=$true, HelpMessage="Your GitHub username (the owner of the fork)")]
    [string]$GithubUsername,

    [string]$UpstreamOwner = "MPDL",
    [string]$UpstreamRepo = "KEEPER",
    [string]$Branch = "feature/self-service-email-migration",
    [string]$BaseBranch = $null   # Will auto-detect if not provided
)

$ErrorActionPreference = "Stop"

$headers = @{
    Authorization = "Bearer $GithubToken"
    "User-Agent"  = "keeper-email-migration-pr-script"
    Accept        = "application/vnd.github+json"
}

Write-Host "=== Self-Service Email Migration PR Creator ===" -ForegroundColor Cyan
Write-Host "Target: $UpstreamOwner/$UpstreamRepo"
Write-Host "Your fork will be under: $GithubUsername"
Write-Host ""

# 1. Detect default branch if not provided
if (-not $BaseBranch) {
    Write-Host "Detecting default branch of $UpstreamOwner/$UpstreamRepo ..."
    try {
        $repoInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/$UpstreamOwner/$UpstreamRepo" -Headers $headers
        $BaseBranch = $repoInfo.default_branch
        Write-Host "Detected default branch: $BaseBranch"
    } catch {
        Write-Warning "Could not auto-detect default branch. Defaulting to 'master'. You can override with -BaseBranch main"
        $BaseBranch = "master"
    }
}

# 2. Create fork (this is safe / idempotent)
Write-Host "Ensuring fork exists under your account..."
try {
    $null = Invoke-RestMethod -Method Post `
        -Uri "https://api.github.com/repos/$UpstreamOwner/$UpstreamRepo/forks" `
        -Headers $headers `
        -Body '{}' -ContentType "application/json" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2  # GitHub sometimes needs a moment
    Write-Host "Fork ready (or already existed)."
} catch {
    # 422 often means it already exists
    Write-Host "Fork request processed (may already exist)."
}

$forkRemoteUrl = "https://x-access-token:${GithubToken}@github.com/${GithubUsername}/${UpstreamRepo}.git"

# 3. Configure remote
Write-Host "Configuring 'fork' remote..."
if ((git remote) -contains "fork") {
    git remote set-url fork $forkRemoteUrl
} else {
    git remote add fork $forkRemoteUrl
}

# 4. Push branch
Write-Host "Pushing branch '$Branch' to your fork (this may take a moment)..."
git push -u fork $Branch --force-with-lease

# 5. Create the Pull Request
Write-Host "Creating Pull Request..."

$prTitle = "feat: Self-service email account migration (phone-move style UX)"

$prBody = Get-Content -Raw -Path "proposed-pr/PR_DESCRIPTION.md"

$body = @{
    title = $prTitle
    head  = "$GithubUsername`:$Branch"
    base  = $BaseBranch
    body  = $prBody
    maintainer_can_modify = $true
} | ConvertTo-Json -Depth 10

try {
    $pr = Invoke-RestMethod -Method Post `
        -Uri "https://api.github.com/repos/$UpstreamOwner/$UpstreamRepo/pulls" `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"

    Write-Host ""
    Write-Host "✅ Pull Request created successfully!" -ForegroundColor Green
    Write-Host "   URL: $($pr.html_url)" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now review, edit the description, or request reviews on GitHub."
} catch {
    $errorBody = $_.ErrorDetails.Message
    if ($errorBody -like "*already exists*") {
        Write-Host "A pull request for this branch already exists." -ForegroundColor Yellow
        Write-Host "You can find it at: https://github.com/$UpstreamOwner/$UpstreamRepo/pulls"
    } else {
        Write-Error "Failed to create PR: $errorBody"
        Write-Host "You can manually open the PR from your fork on GitHub."
    }
}
