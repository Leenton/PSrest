function Save-PSRestCommandResult(){
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$Result,
        [Parameter(Mandatory=$false)]
        [string]$PSRestCommandResultPath = 'C:\PSRest\PSRestCommandResult.json'      
    )
    $Result | ConvertTo-Json | Out-File -FilePath $PSRestCommandResultPath -Encoding UTF8 -Force

}