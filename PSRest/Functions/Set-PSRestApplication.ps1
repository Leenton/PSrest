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