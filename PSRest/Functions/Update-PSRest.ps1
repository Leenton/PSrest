function Update-PSRest(){
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$InstallPath = $Global:InstallPath
    )

    Write-Warning "Ensure PSRest is not running before updating."

    $Activity = 'Updating PSRest'
    Write-Progress -Activity $Activity -Status "Checking for updates..." -PercentComplete 0 -CurrentOperation "Checking for Updates..."

    # Get the current version of the PSRest
    $currentVersion = (Invoke-PSRestConsole -command "--method version" | ConvertFrom-Json).data.version

    # Check if the venv is set if not then create it
    Write-Progress -Activity $Activity -Status "Installing Dependecies..." -PercentComplete 3 -CurrentOperation "Installing Dependencies..."
    if(!(Test-Path "$InstallPath/venv")){
        &python3 -m venv "$InstallPath/venv"
        &pip3 install -r "$InstallPath/config/requirements.txt"
    }
    Write-Progress -Activity $Activity -Status "Checking for new Version of PSRest" -PercentComplete 10 -CurrentOperation "Checking for new Version of PSRest"


    # Get the latest version of the PSRest
    #TODO: Get the latest version from the github repo or psrest.com
    $latestVersion = $currentVersion
    
    if($currentVersion -ne $latestVersion){
        Write-Progress -Activity $Activity -Status "Downloading new PSRest Version" -PercentComplete 15 -CurrentOperation "Downloading..."
        Invoke-Webrequest -Uri psrest.com -OutFile "$InstallPath/PSRest.zip"

        Write-Progress -Activity $Activity -Status "Extracting new PSRest Version" -PercentComplete 50 -CurrentOperation "Extracting..."
        Expand-Archive -Path "$InstallPath/PSRest.zip" -DestinationPath "$InstallPath/PSRest" -Force

        Write-Progress -Activity $Activity -Status "Installing Dependecies" -PercentComplete 60 -CurrentOperation "Installing Dependecies..."
        Remove-Item "$InstallPath/venv" -Recurse -Force -ErrorAction SilentlyContinue
        &python3 -m venv "$InstallPath/venv"
        &pip3 install -r "$InstallPath/config/requirements.txt"

        Write-Progress -Activity $Activity -Status "Patching Databases" -PercentComplete 80 -CurrentOperation "Patching..."
        # Do database patches and delete the venv
        &python3 "$InstallPath/DBPatcher.py"

        # Remove the zip file
        Write-Progress -Activity $Activity -Status "Cleaning up" -PercentComplete 90 -CurrentOperation "Cleaning up..."
        Remove-Item "$InstallPath/PSRest.zip" -Force -ErrorAction SilentlyContinue
        Write-Progress -Activity $Activity -Status "Finished" -PercentComplete 100 -CurrentOperation "Finished"

    }else{
        Write-Progress -Activity $Activity -Status "No Updates Available" -PercentComplete 100 -CurrentOperation "Finished"
    }

    Write-Progress -Activity $Activity -Completed
}