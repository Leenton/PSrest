function Install-PSRestDependencies {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [ValidateSet('debug', 'info', 'warning', 'error', 'critical', 'none')]
        [string]$LogLevel = 'info'
    )

    $ErrorActionPreference = 'Stop'

    Write-Progress -Activity "Initialising PSRest" -Status "Checking dependencies" -PercentComplete 0

    # Check if dependencies are installed
    if (-not (Test-Path $Global:Dependencies)){
        Write-Verbose "PSRest server dependencies are not installed. Installing..."
        Write-Progress -Activity "Initialising PSRest" -Status "Installing dependencies" -PercentComplete 10
        $venv = & $Global:Python -m venv $Global:Dependencies

        # Activate the virtual environment
        Enter-PSRestVirtualEnvironment

        Write-Verbose "Dependencies virtual environment created. Installing dependencies..."
        Write-Progress -Activity "Initialising PSRest" -Status "Installing dependencies" -PercentComplete 20
        
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

    Write-Progress -Activity "Initialising PSRest" -Status "All dependencies installed." -PercentComplete 100

    Write-Progress -Activity "Initialising PSRest" -Completed
}