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