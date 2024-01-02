# Port               : 80
# SSLCertificate     : 
# SSLKeyFile         : 
# SSLKeyFilePassword : 
# SSLCiphers         : 
# DefaultTTL         : 5
# MaxTTL             : 900
# StrictTTL          : False
# ArbitraryCommands  : False
# Help               : True
# Docs               : True
# DefaultDepth       : 4
# StrictDepth        : False

function Set-PSRestConfiguration() {
    [CmdletBinding(SupportsShouldProcess)]
    param (
        [Parameter(Mandatory=$false)]
        [ValidateScript({
            if($_ -gt 0 -and $_ -le 65535){
                return $true
            }else{
                throw "Port must be between 1 and 65535"
            }
        })]
        [int]$Port,
        [Parameter(Mandatory=$false)]
        [ValidateScript({
            if(Test-Path $_){
                return $true
            }else{
                throw "The specified SSL certificate file does not exist."
            }
        })]
        [string]$SSLCertificate,
        [Parameter(Mandatory=$false)]
        [ValidateScript({
            if(Test-Path $_){
                return $true
            }else{
                throw "The specified SSL key file does not exist."
            }
        })]
        [string]$SSLKeyFile,
        [Parameter(Mandatory=$false)]
        [string]$SSLKeyFilePassword,
        [Parameter(Mandatory=$false)]
        [string]$SSLCiphers,
        [Parameter(Mandatory=$false)]
        [ValidateScript({
            if($_ -gt 0){
                return $true
            }else{
                throw "DefaultTTL must be greater than 0"
            }
        })]
        [int]$DefaultTTL,
        [Parameter(Mandatory=$false)]
        [ValidateScript({
            if($_ -gt 0){
                return $true
            }else{
                throw "MaxTTL must be greater than 0"
            }
        })]
        [int]$MaxTTL,
        [Parameter(Mandatory=$false)]
        [bool]$StrictTTL,
        [Parameter(Mandatory=$false)]
        [bool]$ArbitraryCommands,
        [Parameter(Mandatory=$false)]
        [bool]$Help,
        [Parameter(Mandatory=$false)]
        [bool]$Docs,
        [Parameter(Mandatory=$false)]
        [ValidateScript({
            if($_ -gt 0 -and $_ -le 100){
                return $true
            }else{
                throw "DefaultDepth must be greater than 0 and less than or equal to 100"
            }
        })]
        [int]$DefaultDepth,
        [Parameter(Mandatory=$false)]
        [bool]$StrictDepth
    )
    
    try{
        $ConfigJson = Get-Content -Path "$($Global:AppData)/config.json" | ConvertFrom-Json
    }catch{
    }

}