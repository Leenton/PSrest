function Invoke-PSRestCommnd(){
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        [Parameter(Mandatory=$false)]
        [string]$PSRestCommandResultPath = 'C:\PSRest\PSRestCommandResult.json'      
    )
    Invoke-Expression $Command | Tee-Object -FilePath $PSRestCommandResultPath
}
