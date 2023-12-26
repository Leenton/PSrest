function Add-Application  {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        [ValidateSet('client_credential', 'access_token')]
        [string]$Authentication = 'client_credential',
        [Parameter(Mandatory=$true)]
        [string[]]$Cmdlet
    )

}