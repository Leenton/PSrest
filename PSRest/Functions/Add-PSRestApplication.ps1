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