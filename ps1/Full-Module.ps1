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
