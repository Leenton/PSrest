$Global:InstallPath = '/Users/leenton/python/PSrest'
$Global:CheckForUpdates = $true

# Command to invoke the PSRest console to run a command in the console.
function Invoke-PSRestConsole(){
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        # Run the specified command in the consol and return the result.
        [string]$Command
    )

    $FullCommand = '& python3 ./src/ConsoleApp.py ' + $Command
    $result = Invoke-Expression -Command ($FullCommand)

    return $result
}

# Get all the applications registered with the PSRest
function Get-PSRestApplication()
{
    [CmdletBinding(DefaultParameterSetName='Id')]
    param(
        [Parameter(Mandatory=$false, ParameterSetName='Name', Position=0)]
        # The Name of the Application to search for.
        [string]$Name = '',

        [Parameter(Mandatory=$false, ParameterSetName='Id', Position=0)]
        # The Id of the Application to search for.
        [int32]$Id = 0
    )
    
    if ($Name -or $Id){
        if($Id){
            $result = Invoke-PSRestConsole -command "--method get --id $Id"
        }
        else{
            $result = Invoke-PSRestConsole -command "--method get --name '$Name'"
        }
    }else{
        $result = Invoke-PSRestConsole -command "--method get"
    }

    try{
        $application = ConvertFrom-Json $result
    }catch {
        throw "Error occured attempting to get the specified application(s)."
    }

    if (!$application.data -and $Name){
        throw "The application '$Name' does not exist."
    }elseif($application.data -eq 'invalid'){
        throw "An Id and Name cannot be specified at the same time."
    }

    return $application.data
}

# Remove the specified application
function Remove-PSRestApplication()
{
    [CmdletBinding(DefaultParameterSetName='Id')]
    param(
        [Parameter(Mandatory=$false, ParameterSetName='Id', Position=0)]
        # The Id of the Application to remove
        [int32]$Id,
        [Parameter(Mandatory=$false, ParameterSetName='Name', Position=0)]
        # The name of the application to remove
        [string]$Name

    )

    try{
        if($Name){
            $application = Get-PSRestApplication -Name $Name
            if(!$application){
                throw "The application '$Name' does not exist."
            }
            $Id = $application.id
        }

        $result = Invoke-PSRestConsole -command "--method remove --id $Id"

        $result = $result | ConvertFrom-Json
        if($result.data -eq $true){
            return
        }
    }catch{
        throw $result
    }

    throw "The Application specified does not exist."
}

# Add a new application
function Add-PSRestApplication()
{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        # The name of the application
        [string]$Name,
        # The description of the application
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        # The type of authentication to use, either 'client_credential' or 'access_token'. Note that 'access_token' is not recommended for security reasons.
        [ValidateSet('client_credential', 'access_token')]
        [string]$Authentication = 'client_credential',
        [Parameter(Mandatory=$true)]
        # The cmdlets the application is permitted to use.
        [string[]]$Cmdlet
    )

    #Check that the description is no more than 10^9 bytes long when encoded as UTF-8
    if ($Description){
        $DescriptionBytes = [System.Text.Encoding]::UTF8.GetBytes($Description)
        if ($DescriptionBytes.Length -gt 1000000000){
            throw "The description is too long. The description must be no more than 10^9 bytes long when encoded as UTF-8."
        }
    }

    # Verify tha the specified cmdlets exist on the system.
    $Cmdlets = @()
    foreach ($cmdlet in $Cmdlet){
        $command = Get-Command $cmdlet -ErrorAction SilentlyContinue
        if ($command){
            $Cmdlets += $cmdlet
        }else{
            throw "The cmdlet '$cmdlet' does not exist on the system."
        }
    }

    # Verify that the application does not already exist.
    $existingApplication = Get-PSRestApplication -Name $Name -ErrorAction SilentlyContinue
    if ($existingApplication){
        throw "The application '$Name' already exists."
    }

    $result = Invoke-PSRestConsole -command  "--method add --name '$Name' --description '$Description' --authentication '$Authentication' --actions '$($Cmdlets -join ',')'"
    # $result = Invoke-Expression -Command ('& ' + (Get-PSRestApplicationPath) +  "--method add --name '$Name' --description '$Description' --authentication '$Authentication' --cmdlet '$($Cmdlets -join ',')'")
    
    try{
        $application = ConvertFrom-Json $result
        return $application.data
    }catch{
        throw "Error occured attempting to add the specified application."
    }
}

# Modify the specified application
function Set-PSRestApplication()
{
    [CmdletBinding(DefaultParameterSetName='Id')]
    param
    (
        [Parameter(Mandatory=$true, ParameterSetName='Name', Position=0)]
        # The name of the application
        [string]$Name,
        [Parameter(Mandatory=$true, ParameterSetName='Id', Position=0)]
        # The name of the application
        [string]$Id,
        # The description of the application
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        # The cmdlets the application is permitted to use.
        [string[]]$Cmdlet
    )

    #Check that the description is no more than 10^9 bytes long when encoded as UTF-8
    if ($Description)
    {
        $DescriptionBytes = [System.Text.Encoding]::UTF8.GetBytes($Description)
        if ($DescriptionBytes.Length -gt 1000000000)
        {
            throw "The description is too long. The description must be no more than 10^9 bytes long when encoded as UTF-8."
        }
    }

    # Verify tha the specified cmdlets exist on the system.
    $Cmdlets = @()
    foreach ($Cmd in $Cmdlet)
    {
        $Command = Get-Command $Cmd -ErrorAction SilentlyContinue
        if ($Command)
        {
            $Cmdlets += $Cmd
        }
        else
        {
            throw "The cmdlet '$Cmd' does not exist on the system."
        }
    }

    try{
        if($Name){
            $application = Get-PSRestApplication -Name $Name -ErrorAction SilentlyContinue
            if(!$application){
                throw "The application '$Name' does not exist."
            }
            $Id = $application.id
        }else{
            $application = Get-PSRestApplication -Id $Id -ErrorAction SilentlyContinue
            if(!$application){
                throw "The application with id '$Id' does not exist."
            }
        }

        $result = Invoke-PSRestConsole -command "--method set --id $Id $($Description ? "--description '$Description' " : '')$($Cmdlets ? "--actions $($Cmdlets -join ',')" : '' )"
        $application = ConvertFrom-Json $result

        if($application.data -eq $true){
            return
        }else{
            throw "Error occured attempting to modify the specified application."
        }

    }catch{
        throw "Error occured attempting to modify the specified application."
    }

}

# Processor that executes the commands recieved by the API
function Start-PSRestProcessor {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$ProcessorId,
        [Parameter(Mandatory = $true)]
        [string]$SocketPath,
        [Parameter(Mandatory = $true)]
        [string]$ResponseDirectory,
        [Parameter(Mandatory = $true)]
        [int]$WaitTime = 250
    )


    begin{
        
    }

    process{
        import-Module '/Users/leenton/c#/PSRestModule/PSRestModule/bin/Debug/net7.0/PSRestModule.dll'
        
        trap{
            if(!$command){
                #Process failed but no command was received, so it doesn't matter just exit
                exit 
            }

            #If we have a response try again, and if we fail again just exit
            try {
                Send-PSRestResponse -Ticket $command.Ticket -ResponseDirectory $ResponseDirectory -InputObject $Response -WaitTime $WaitTime
            }
            catch {
                exit
            }
        }
    
        while($true){
            #Get the command to execute
            $Command = Receive-PSRestCommand -SocketPath $SocketPath -ProcessorId $ProcessorId

            #Try and execute the command and send the result back
            try{
                $Data = Invoke-Expression -Command $Command 
            }
            catch {
                $Exception = $_.Exception.Message
            }

            #Convert the data to json
            $Response = @{
                data = $Data;
                error = $Exception
            } | ConvertTo-Json -Depth $command.Depth

            #Send the response over the wire
            Send-PSRestResponse -Ticket $command.Ticket -ResponseDirectory $ResponseDirectory -InputObject $Response -WaitTime $WaitTime
            $Command = $null
        }
    }
}

# Install updates for the PSRest
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
        &pip3 install -r "$InstallPath/src/config/requirements.txt"
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
        &pip3 install -r "$InstallPath/src/config/requirements.txt"

        Write-Progress -Activity $Activity -Status "Patching Databases" -PercentComplete 80 -CurrentOperation "Patching..."
        # Do database patches and delete the venv
        &python3 "$InstallPath/src/DBPatcher.py"

        # Remove the zip file
        Write-Progress -Activity $Activity -Status "Cleaning up" -PercentComplete 90 -CurrentOperation "Cleaning up..."
        Remove-Item "$InstallPath/PSRest.zip" -Force -ErrorAction SilentlyContinue
        Write-Progress -Activity $Activity -Status "Finished" -PercentComplete 100 -CurrentOperation "Finished"

    }else{
        Write-Progress -Activity $Activity -Status "No Updates Available" -PercentComplete 100 -CurrentOperation "Finished"
    }

    Write-Progress -Activity $Activity -Completed
}

# Start the PSRest server
function Start-PSRest(){
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $false)]
        [int]$Port,
        [Parameter(Mandatory = $false)]
        [int]$Workers,
        [Parameter(Mandatory = $false)]
        [string]$LogLevel
    )

    $PSRestQueue = "PSRestQueue"

    # Do any database patches if the version has changed
    Update-PSRest -WarningAction SilentlyContinue

    # Get the current directory so we can return to it after exiting PSRest
    $CurrentDirectory = Get-Location

    try{
        Set-Location $Global:InstallPath
        # Start the PSRestqQeue as it's shared between all the processors and workers
        Get-Job -Name $PSRestQueue -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue
        $Job = Start-Job -ScriptBlock { &python3 ./src/Queue.py } -Name $PSRestQueue

        # Start the PSRest Workers
        &python3 ./src/App.py
    }finally{
        # Stop the Queue as the workers have exited and we don't need it anymore
        Remove-Job -Name $PSRestQueue -Force -ErrorAction SilentlyContinue

        # Return to the original directory
        Set-Location $CurrentDirectory
    }
}

# Get all the commands that are available to the PSRest application
function Get-PSRestCommandLibrary{

    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        # The modules to get the commands from
        [string[]]$Module,
        [Parameter(Mandatory=$false)]
        # The commands that are not in the specified modules which should be included in the library
        [string[]]$EnabledCommands,
        [Parameter(Mandatory=$false)]
        # The commands that are in the specified modules which should be excluded from the library
        [string[]]$DisabledCommands,

        [Parameter(Mandatory=$true)]
        # The string to use to prepened to the returned base64 output for capture. 
        [string]$Seperator
    )

    process{

        $Commands = @()

        if($Module -eq '*'){
            $ModuleCommands = Get-Command
        }else{
            foreach($Mod in $Module){
                $ModuleCommands += Get-Command -Module $Mod
            }
        }
        
        # Remove the commands that are in the disabled list
        foreach($Command in $ModuleCommands){
            if($DisabledCommands -notcontains $Command.Name){
                $Commands += $Command
            }
        }

        # Add the commands that are in the enabled list
        foreach($Command in $EnabledCommands){
            $Commands += Get-Command -Name $Command 
        }

        #Get only the unique commands in the Commands array so we don't reprocess data
        $Commands = $Commands | Sort-Object -Property Name -Unique
        
        #Get the help file for each command
        $Commands = foreach($Command in $Commands){
            try{
                $Help = Get-Help -Name $Command.Name -Full 
                $Mandatory = if($Help.Parameters.Parameter | Where-Object {
                    $_.Required -eq $true
                }){
                    $true
                }else{
                    $false
                }

                @{
                    Name = $Command.Name
                    MandatoryParameters = $Mandatory
                    Module = $Command.Source
                    Version = $Command.Version
                    Help = $Help | Out-String
                }
            }catch{
                continue
            }
        }
        
        if($Commands.count -gt 1){
            $Commands =  $Commands | ConvertTo-Json
        }elseif($Commands.count -eq 1){
            $Commands =  @($Commands) | ConvertTo-Json
        }else{
            $Commands =  @() | ConvertTo-Json
        }
        
        Write-host "$Seperator$([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Commands)))"
    }
}





#TODO: Remove this
$client = @{client_id='36c9adc3-f9da-4170-b087-a3eaa14e14b3'; client_secret='1c051bd3-ec5d-479c-b777-60e5e92cbf5a'; grant_type="client_credential";}
$token = Invoke-WebRequest -Uri http://localhost/oauth -Method POST -Body $client 
$header = @{Authorization = "Bearer $(($token.content | ConvertFrom-Json).accesstoken)"}

Invoke-WebRequest -Method Post -Headers $header -Uri http://localhost/run -Body (@{cmdlet="Write-Host"} | convertto-json)  -ContentType application/json