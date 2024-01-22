function Start-PSRest(){
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $false)]
        [int]$Port,
        [Parameter(Mandatory = $false)]
        [ValidateSet('debug', 'info', 'warning', 'error', 'critical', 'none')]
        [string]$LogLevel = 'info'

    )

    $ErrorActionPreference = 'Stop'

    # Activate the virtual environment
    Enter-PSRestVirtualEnvironment

    if ($Port -gt 65535 -or $Port -lt 1 -and ($Port -ne 0)){
        throw "The port must be a positive whole number less than 65536."
    }

    try{
        # Start the PSRest Workers
        &$($Global:Python) ($Global:InstallPath + '/' + "App.py") --port=$Port --loglevel=$LogLevel
    }finally{
        # Deactivate the virtual environment
        Exit-PSRestVirtualEnvironment
    }
}