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