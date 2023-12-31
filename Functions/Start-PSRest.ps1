function Start-PSRest(){
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $false)]
        [int]$Port,
        [Parameter(Mandatory = $false)]
        [ValidateSet('debug', 'info', 'warning', 'error', 'critical', 'none')]
        [string]$LogLevel = 'info'

    )

    if ($Port -gt 65535 -or $Port -lt 1 -and ($Port -ne 0)){
        throw "The port must be a positive whole number less than 65536."
    }

    # Do any database patches if the version has changed
    # Update-PSRest -WarningAction SilentlyContinue

    try{
        # Start the PSRest Workers
        &python3 ($Global:InstallPath + '/' + "App.py") --port=$Port --loglevel=$LogLevel
    }finally{
    }
}