function Get-PSRestApplication()
{
    [CmdletBinding()]
    param
    (
        [Parameter(Mandatory=$false)]
        # The name of the application
        [string]$Name
    )
    

    if ($Name)
    {
        $result = & "python3 src/ConsoleApp.py --get $Name"
    }
    else
    {
        $result = & "python3 src/ConsoleApp.py --get"
    }

    $application = ConvertFrom-Json $result

    if (!$application -and $Name)
    {
        throw "The application '$Name' does not exist."
    }

    return $application
}

function Add-PSRestApplication()
{
    [CmdletBinding()]
    param
    (
        [Parameter(Mandatory=$true)]
        # The name of the application
        [string]$Name,
        # The description of the application
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        # The type of authentication to use, either 'client_credentials' or 'access_token'. Note that 'access_token' is not recommended for security reasons.
        [ValidateSet('client_credentials', 'access_token')]
        [string]$AuthType = 'client_credentials',
        [Parameter(Mandatory=$true)]
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
    foreach ($cmdlet in $Cmdlet)
    {
        $command = Get-Command $cmdlet -ErrorAction SilentlyContinue
        if ($command)
        {
            $Cmdlets += $cmdlet
        }
        else
        {
            throw "The cmdlet '$cmdlet' does not exist on the system."
        }
    }

    # Verify that the application does not already exist.
    $existingApplication = Get-PSRestApplication -Name $Name -ErrorAction SilentlyContinue
    if ($existingApplication)
    {
        throw "The application '$Name' already exists."
    }


    $result = & "python3 src/ConsoleApp.py --add-application --name $Name --description $Description --auth-type $AuthType --cmdlet $Cmdlets"
    $application = ConvertFrom-Json $result
    return $application
}

function Remove-PSRestApplication()
{
    [CmdletBinding()]
    param
    (
        [Parameter(Mandatory=$true)]
        # The name of the application
        [string]$Name
    )

    $result = & "python3 src/ConsoleApp.py --remove-application --name $Name"
    $application = ConvertFrom-Json $result
    return $application
}

function Set-PSRestApplication()
{
    [CmdletBinding()]
    param
    (
        [Parameter(Mandatory=$true)]
        # The name of the application
        [string]$Name,
        # The description of the application
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        # The type of authentication to use, either 'client_credentials' or 'access_token'. Note that 'access_token' is not recommended for security reasons.
        [ValidateSet('client_credentials', 'access_token')]
        [string]$AuthType,
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
    foreach ($cmdlet in $Cmdlet)
    {
        $command = Get-Command $cmdlet -ErrorAction SilentlyContinue
        if ($command)
        {
            $Cmdlets += $cmdlet
        }
        else
        {
            throw "The cmdlet '$cmdlet' does not exist on the system."
        }
    }

    # Verify that the application exists.
    $existingApplication = Get-PSRestApplication -Name $Name -ErrorAction SilentlyContinue
    if (!$existingApplication)
    {
        throw "The application '$Name' does not exist."
    }

    $result = & "python3 src/ConsoleApp.py --set-application --name $Name --description $Description --auth-type $AuthType --cmdlet $Cmdlets"
    $application = ConvertFrom-Json $result
    return $application
}