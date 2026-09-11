#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy-backup helpers: NAS backup-root resolution, guarded snapshot removal, keep-N rotation.
.DESCRIPTION
    Defines FUNCTIONS ONLY. Nothing runs at load time, so a test harness can dot-source this
    file against fake directories. scripts/deploy_to_custommaps.ps1 dot-sources it after
    _common.ps1 (which supplies $Config and $RepoRoot).

    R-259 (Will 2026-09-10, verbatim): "why do we have a 300gb backups tree? no wonder i have
    no disk space" / "if you need to save backups like this move them to the network drive."
    Cause: deploy_to_custommaps.ps1 copied the ENTIRE deployed mod (~1.3 GB) into the repo's
    backups\deployed\<mod>\<timestamp>\ on EVERY deploy with NO rotation (only the character
    snapshots had a keep-10). Now every snapshot lives under WIN_BACKUP_ROOT (a network-drive
    path, REQUIRED, no local fallback) and only the newest N per mod are kept (BACKUP_KEEP,
    default 5).

    The rotation DELETE is guarded, because on 2026-09-09 a recursive delete followed a Windows
    junction and emptied the build inputs it pointed at (docs/MISTAKES.md 2026-09-09, guard 1).
    Before any snapshot directory is removed, every assertion in Test-BackupSnapshotRemovable
    must hold; a failing assertion SKIPS that snapshot with a loud warning and never deletes.

    Layout under the root:
      <root>\deployed\<mod>\<yyyyMMdd_HHmmss>\   one per deploy, newest BACKUP_KEEP kept
      <root>\characters\<yyyyMMdd_HHmmss>\      one per deploy, newest 10 kept

    Hardened after the independent vet of 8ba96e2 (R-259 findings F1-F5): the root must be FULLY
    qualified and free of reparse points on its whole path, the guard's ancestor walk runs to the
    drive root, the deploy target's junction refusal runs before the snapshot copy, and a snapshot
    is verified by file count AND total bytes.
#>

Set-StrictMode -Version Latest

# Snapshot directories are named yyyyMMdd_HHmmss by deploy_to_custommaps.ps1. The rotation only
# ever counts or removes directories matching this, so a stray directory under the backup root
# is neither rotated out nor mistaken for a snapshot, and the <kind> / <mod> directories can
# never be a delete candidate.
$script:BackupSnapshotNameRe = '^\d{8}_\d{6}$'

function Get-BackupFullPath {
    <# Absolute path with any trailing separator removed, so prefix comparisons are exact. #>
    param([Parameter(Mandatory = $true)][string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)
    return $full.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
}

function Test-BackupReparsePoint {
    <# $true when the item carries the ReparsePoint attribute (junction, symlink, mount point). #>
    param([Parameter(Mandatory = $true)][System.IO.FileSystemInfo]$Item)
    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Get-BackupPathReparseAncestor {
    <#
    .SYNOPSIS
        The FIRST reparse point on $Path itself or on any ancestor up to the drive root, else $null.
    .DESCRIPTION
        Walks $Path, then its parent, then its parent, all the way to the drive root (NOT stopping
        at the backup root: the root can itself sit under a junction, and then every "contained"
        path below it is a foreign tree by string prefix alone). Components that do not exist are
        skipped, so this can be called on a root that is about to be created. A component that
        cannot be read throws, which callers treat as "cannot prove safe".
    #>
    param([Parameter(Mandatory = $true)][string]$Path)
    $cursor = Get-BackupFullPath -Path $Path
    $driveRoot = Get-BackupFullPath -Path ([System.IO.Path]::GetPathRoot($cursor))
    while ($cursor -and ($cursor.Length -ge $driveRoot.Length)) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
            if (Test-BackupReparsePoint -Item $item) { return $item }
        }
        $parent = Split-Path -Parent $cursor
        if ((-not $parent) -or ($parent -eq $cursor)) { break }
        $cursor = $parent
    }
    return $null
}

function Get-BackupReparsePoints {
    <#
    .SYNOPSIS
        Every reparse point at or below $Path, including $Path itself.
    .DESCRIPTION
        If $Path itself is a reparse point it is returned alone: enumerating below it would walk
        the link TARGET, which is exactly the tree a delete must never reach.
    #>
    param([Parameter(Mandatory = $true)][string]$Path)
    # Results are emitted UNROLLED (never `return ,$array`): callers wrap in @(), and a comma-
    # wrapped empty array would come back as ONE element, which the first sandbox run proved
    # makes the guard refuse every clean snapshot.
    $self = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (Test-BackupReparsePoint -Item $self) { return $self }
    $below = @(Get-ChildItem -LiteralPath $Path -Recurse -Force -Attributes ReparsePoint -ErrorAction Stop)
    return $below
}

function Get-BackupLinkDirectories {
    <#
    .SYNOPSIS
        Directory junctions and directory symbolic links at or below $Path (LinkType-based).
    .DESCRIPTION
        The narrower check used before the deploy target is removed. The deploy target lives
        under OneDrive, and OneDrive Files-On-Demand placeholders can carry the ReparsePoint
        attribute without being links, so an attribute-only refusal there could block every
        deploy for no reason. The two shapes whose recursive delete reaches a FOREIGN tree are
        directory junctions (LinkType 'Junction') and directory symbolic links (LinkType
        'SymbolicLink'). Measured 2026-09-10: the 20 reparse-point directories under
        Documents\My Games (all in Working\CustomMaps\BCBake) report LinkType 'Junction', so
        this check catches exactly the 2026-09-09 shape.
    #>
    param([Parameter(Mandatory = $true)][string]$Path)
    # Emitted unrolled (see Get-BackupReparsePoints); callers wrap in @().
    $self = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($self.PSIsContainer -and $self.LinkType -and $self.LinkType -in @('Junction', 'SymbolicLink')) {
        return $self
    }
    $below = @(Get-ChildItem -LiteralPath $Path -Recurse -Force -Directory -Attributes ReparsePoint -ErrorAction Stop |
        Where-Object { $_.LinkType -and $_.LinkType -in @('Junction', 'SymbolicLink') })
    return $below
}

function Resolve-BackupRoot {
    <#
    .SYNOPSIS
        Validate WIN_BACKUP_ROOT and return its absolute path, or THROW (fail loud).
    .DESCRIPTION
        Throws when the value is empty or not FULLY QUALIFIED, when it lies inside the repo (the
        exact tree R-259 retired), when it or any ancestor up to the drive root is a reparse point,
        when neither it nor its parent exists (the network drive is not mounted), or when a probe
        file cannot be written there. Creates the root itself when only its parent exists (the
        first deploy onto the drive). There is deliberately NO fallback to a local path: a missing
        NAS must stop the deploy, not quietly refill C:.

        "Fully qualified" is stricter than [IO.Path]::IsPathRooted, which accepts the two shapes
        that resolve against the CURRENT DIRECTORY: drive-relative 'C:foo' and root-relative
        '\foo'. Either would silently build a backup tree wherever the shell happened to be (the
        vet of 8ba96e2 watched 'C:relative' create one), so both are refused.
    #>
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Root,
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )
    $trimmed = $Root.Trim()
    if (-not $trimmed) { throw 'WIN_BACKUP_ROOT is empty.' }
    if ($trimmed -notmatch '^([A-Za-z]:\\|\\\\)') {
        throw "WIN_BACKUP_ROOT must be a FULLY QUALIFIED path - a drive path 'Z:\Computer Backup\...' or a UNC path '\\server\share\...' (got '$trimmed'). A drive-relative 'C:foo' or root-relative '\foo' resolves against the current directory and would create a backup tree wherever the shell happened to be."
    }
    $full = Get-BackupFullPath -Path $trimmed
    $repoFull = Get-BackupFullPath -Path $RepoRoot
    $cmp = [System.StringComparison]::OrdinalIgnoreCase
    if ($full.Equals($repoFull, $cmp) -or $full.StartsWith("$repoFull\", $cmp)) {
        throw "WIN_BACKUP_ROOT '$full' is inside the repo '$repoFull'. R-259: deploy backups live on the network drive, never under the repo (that tree reached ~300 GB on C:)."
    }
    # Checked BEFORE the root is created: a root that is a reparse point, or that sits under one,
    # makes every snapshot "under the root" a foreign tree by string prefix alone, and the rotation
    # delete would reach whatever the link points at (docs/MISTAKES.md 2026-09-09, guard 1).
    $linkAncestor = Get-BackupPathReparseAncestor -Path $full
    if ($linkAncestor) {
        throw "WIN_BACKUP_ROOT '$full' is refused: '$($linkAncestor.FullName)' on its path is a reparse point (junction, symlink or mount point). Rotation deletes under a linked root would reach a foreign tree. Point WIN_BACKUP_ROOT at a real directory (R-259, docs/MISTAKES.md 2026-09-09)."
    }
    if (-not (Test-Path -LiteralPath $full -PathType Container)) {
        $parent = Split-Path -Parent $full
        if (-not $parent -or -not (Test-Path -LiteralPath $parent -PathType Container)) {
            throw "WIN_BACKUP_ROOT '$full' is unreachable: neither it nor its parent exists. Is the network drive mounted? There is deliberately NO local fallback (R-259)."
        }
        [void][System.IO.Directory]::CreateDirectory($full)
    }
    $probe = Join-Path $full ".write_probe_$([guid]::NewGuid().ToString('N'))"
    try {
        [System.IO.File]::WriteAllText($probe, 'probe')
        Remove-Item -LiteralPath $probe -Force -ErrorAction Stop
    } catch {
        throw "WIN_BACKUP_ROOT '$full' is not writable: $($_.Exception.Message) (R-259: no local fallback)."
    }
    return $full
}

function Get-BackupKeep {
    <# BACKUP_KEEP from the config hashtable: optional, default 5, must be a positive integer. #>
    param(
        [Parameter(Mandatory = $true)][hashtable]$Config,
        [int]$Default = 5
    )
    $raw = $null
    if ($Config.ContainsKey('BACKUP_KEEP')) { $raw = $Config['BACKUP_KEEP'] }
    if (-not $raw) { return $Default }
    $n = 0
    if (-not [int]::TryParse([string]$raw, [ref]$n) -or $n -lt 1) {
        throw "BACKUP_KEEP must be a positive integer (got '$raw'). A keep of 0 would delete the snapshot just written."
    }
    return $n
}

function Test-BackupSnapshotRemovable {
    <#
    .SYNOPSIS
        THE DELETE GUARD. $true only when every assertion holds; otherwise warns and returns $false.
    .DESCRIPTION
        (i)   containment: the absolute path starts with <root>\<kind>\ and is deeper than it;
        (i-b) the leaf is a yyyyMMdd_HHmmss snapshot name (never the <kind> or <mod> dir itself);
        (ii)  no directory from the snapshot's parent up to the DRIVE ROOT is a reparse point (a
              junctioned <mod> directory, or a junction ABOVE the backup root itself, would make a
              foreign tree look contained by string prefix alone);
        (iii) the snapshot is not a reparse point and contains none
              (Get-ChildItem -Recurse -Force -Attributes ReparsePoint returns nothing).
        Any exception while checking counts as "cannot prove safe" and refuses.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][ValidateSet('deployed', 'characters')][string]$Kind,
        [Parameter(Mandatory = $true)][string]$Path
    )
    try {
        $rootFull = Get-BackupFullPath -Path $Root
        $pathFull = Get-BackupFullPath -Path $Path
        $prefix = "$rootFull\$Kind\"
        $cmp = [System.StringComparison]::OrdinalIgnoreCase

        if ((-not $pathFull.StartsWith($prefix, $cmp)) -or ($pathFull.Length -le $prefix.Length)) {
            Write-Warning "ROTATION SKIP (outside root): '$pathFull' is not under '$prefix'. NOT deleted."
            return $false
        }
        $leaf = Split-Path -Leaf $pathFull
        if ($leaf -notmatch $script:BackupSnapshotNameRe) {
            Write-Warning "ROTATION SKIP (not a snapshot name): leaf '$leaf' of '$pathFull' is not yyyyMMdd_HHmmss. NOT deleted."
            return $false
        }
        if (-not (Test-Path -LiteralPath $pathFull -PathType Container)) {
            Write-Warning "ROTATION SKIP (missing): '$pathFull' is not a directory. NOT deleted."
            return $false
        }
        # The walk goes all the way to the DRIVE ROOT, not only down to $rootFull: if the backup
        # root itself sits under a junction, every path "inside" it is a foreign tree and stopping
        # at the root would never see the link.
        $linkAncestor = Get-BackupPathReparseAncestor -Path (Split-Path -Parent $pathFull)
        if ($linkAncestor) {
            Write-Warning "ROTATION SKIP (junction on the path): '$($linkAncestor.FullName)' is a reparse point, so '$pathFull' may be a foreign tree. NOT deleted."
            return $false
        }
        $links = @(Get-BackupReparsePoints -Path $pathFull)
        if ($links.Count -gt 0) {
            $shown = (@($links | Select-Object -First 3 | ForEach-Object { $_.FullName })) -join '; '
            Write-Warning "ROTATION SKIP (reparse point): '$pathFull' is or contains $($links.Count) junction/symlink(s): $shown. NOT deleted (docs/MISTAKES.md 2026-09-09)."
            return $false
        }
        return $true
    } catch {
        Write-Warning "ROTATION SKIP (guard error): could not prove '$Path' safe to delete: $($_.Exception.Message). NOT deleted."
        return $false
    }
}

function Remove-BackupSnapshot {
    <# Guarded recursive delete of ONE snapshot directory. Returns $true if removed, $false if refused. #>
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][ValidateSet('deployed', 'characters')][string]$Kind,
        [Parameter(Mandatory = $true)][string]$Path
    )
    if (-not (Test-BackupSnapshotRemovable -Root $Root -Kind $Kind -Path $Path)) { return $false }
    $pathFull = Get-BackupFullPath -Path $Path
    Remove-Item -LiteralPath $pathFull -Recurse -Force -ErrorAction Stop
    return $true
}

function Invoke-BackupRotation {
    <#
    .SYNOPSIS
        Keep the newest $Keep snapshots under <root>\<kind>[\<subpath>]; remove the rest, guarded.
    .DESCRIPTION
        Snapshots are the directories whose name matches yyyyMMdd_HHmmss, sorted by name
        descending (the name IS the timestamp). Returns an object with Dir, Kept, Removed and
        Skipped (guard-refused) name lists. Never throws for a refused snapshot; throws only for
        an invalid $Keep.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][ValidateSet('deployed', 'characters')][string]$Kind,
        [string]$SubPath = '',
        [Parameter(Mandatory = $true)][int]$Keep
    )
    if ($Keep -lt 1) {
        throw "Invoke-BackupRotation: Keep must be >= 1 (got $Keep); a keep of 0 would delete the snapshot just written."
    }
    $dir = Join-Path $Root $Kind
    if ($SubPath) { $dir = Join-Path $dir $SubPath }
    $result = [pscustomobject]@{ Dir = $dir; Kept = @(); Removed = @(); Skipped = @() }
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) { return $result }

    $snaps = @(Get-ChildItem -LiteralPath $dir -Directory -Force -ErrorAction Stop |
        Where-Object { $_.Name -match $script:BackupSnapshotNameRe } |
        Sort-Object Name -Descending)
    if ($snaps.Count -le $Keep) {
        $result.Kept = @($snaps | ForEach-Object { $_.Name })
        return $result
    }
    $result.Kept = @($snaps[0..($Keep - 1)] | ForEach-Object { $_.Name })
    foreach ($old in $snaps[$Keep..($snaps.Count - 1)]) {
        if (Remove-BackupSnapshot -Root $Root -Kind $Kind -Path $old.FullName) {
            $result.Removed += $old.Name
        } else {
            $result.Skipped += $old.Name
        }
    }
    return $result
}

function Test-BackupCopyVerified {
    <#
    .SYNOPSIS
        Compare a copy against its source by FILE COUNT and TOTAL BYTES. Returns a result object.
    .DESCRIPTION
        docs/MISTAKES.md 2026-09-09, guard 4: verify a copy by content measures, never by exit
        status. A count match alone passes a copy that truncated a file mid-transfer (a real SMB
        failure mode), so the byte total is compared beside it. Returns
        @{ Ok; Reason; SourceFiles; DestFiles; SourceBytes; DestBytes } and never throws for a
        mismatch; the caller decides how loudly to fail.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    $srcFiles = @(Get-ChildItem -LiteralPath $Source -Recurse -File -Force -ErrorAction Stop)
    $dstFiles = @(Get-ChildItem -LiteralPath $Destination -Recurse -File -Force -ErrorAction Stop)
    $srcBytes = [int64](($srcFiles | Measure-Object -Property Length -Sum).Sum)
    $dstBytes = [int64](($dstFiles | Measure-Object -Property Length -Sum).Sum)
    $reason = ''
    if ($dstFiles.Count -ne $srcFiles.Count) {
        $reason = "backup verification failed: file count mismatch (src $($srcFiles.Count), dst $($dstFiles.Count))"
    } elseif ($dstBytes -ne $srcBytes) {
        $reason = "backup verification failed: total bytes mismatch (src $srcBytes, dst $dstBytes)"
    }
    return [pscustomobject]@{
        Ok          = [bool](-not $reason)
        Reason      = $reason
        SourceFiles = $srcFiles.Count
        DestFiles   = $dstFiles.Count
        SourceBytes = $srcBytes
        DestBytes   = $dstBytes
    }
}

function Save-BackupDeploySnapshot {
    <#
    .SYNOPSIS
        Snapshot $Source into $Destination, junction-refused FIRST and verified by count + bytes.
    .DESCRIPTION
        The order is the whole point (vet of 8ba96e2, finding F3): the junction refusal runs BEFORE
        anything is created or copied, so a junctioned deploy target is never dragged across SMB
        and no empty snapshot directory is left behind. Then the copy runs, then
        Test-BackupCopyVerified must pass. Throws on a refusal or a verification failure, so the
        caller still holds an untouched $Source; returns @{ Path; Files; Bytes } on success.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    $srcFull = Get-BackupFullPath -Path $Source
    if (-not (Test-Path -LiteralPath $srcFull -PathType Container)) {
        throw "Save-BackupDeploySnapshot: source '$srcFull' is not a directory."
    }
    $links = @(Get-BackupLinkDirectories -Path $srcFull)
    if ($links.Count -gt 0) {
        throw "'$srcFull' is or contains $($links.Count) directory junction/symlink(s) (first: $($links[0].FullName)). Refusing to snapshot or delete it; remove the link(s) by hand and re-run (docs/MISTAKES.md 2026-09-09)."
    }
    $dstFull = Get-BackupFullPath -Path $Destination
    if (-not (Test-Path -LiteralPath $dstFull -PathType Container)) {
        [void][System.IO.Directory]::CreateDirectory($dstFull)
    }
    Copy-Item -Path (Join-Path $srcFull '*') -Destination $dstFull -Recurse -Force -ErrorAction Stop
    $verify = Test-BackupCopyVerified -Source $srcFull -Destination $dstFull
    if (-not $verify.Ok) {
        throw "$($verify.Reason) copying '$srcFull' to '$dstFull'. Nothing was removed."
    }
    return [pscustomobject]@{ Path = $dstFull; Files = $verify.DestFiles; Bytes = $verify.DestBytes }
}
