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


    Write-Progress -Activity "Starting PSRest Server" -Status "Checking dependencies" -PercentComplete 0

    # Check if dependencies are installed
    if (-not (Test-Path $Global:Dependencies)){
        Write-Verbose "PSRest server dependencies are not installed. Installing..."
        Write-Progress -Activity "Starting PSRest Server" -Status "Installing dependencies" -PercentComplete 10
        $venv = & $Global:Python -m venv $Global:Dependencies

        # Activate the virtual environment
        Enter-PSRestVirtualEnvironment

        Write-Verbose "Dependencies virtual environment created. Installing dependencies..."
        Write-Progress -Activity "Starting PSRest Server" -Status "Installing dependencies" -PercentComplete 20
        
        # Install the dependencies
        if ($Global:Platform -eq 'Windows'){
            $dependencies = & $Global:Python -m pip install -r "$($Global:InstallPath)/configuration/requirements.txt" --disable-pip-version-check --root-user-action=ignore
        }else{
            $dependencies = & pip install -r "$($Global:InstallPath)/configuration/requirements.txt" --disable-pip-version-check --root-user-action=ignore
        }
        Write-Verbose "Dependencies installed."
        
        # Deactivate the virtual environment
        Exit-PSRestVirtualEnvironment
    }

    Write-Progress -Activity "Starting PSRest Server" -Status "All dependencies installed." -PercentComplete 100

    # # Activate the virtual environment
    # Enter-PSRestVirtualEnvironment

    # Write-Progress -Activity "Starting PSRest Server" -Status "Patching DB..." -PercentComplete 0

    # &$($Global:Python) ($Global:InstallPath + '/' + "DatabasePatcher.py")



    # # Do any database patches if the version has changed
    # # Update-PSRest -WarningAction SilentlyContinue

    # if ($Port -gt 65535 -or $Port -lt 1 -and ($Port -ne 0)){
    #     throw "The port must be a positive whole number less than 65536."
    # }

    # try{
    #     # Start the PSRest Workers
    #     &$($Global:Python) ($Global:InstallPath + '/' + "App.py") --port=$Port --loglevel=$LogLevel
    # }finally{
    #     # Deactivate the virtual environment
    #     Exit-PSRestVirtualEnvironment
    # }
}