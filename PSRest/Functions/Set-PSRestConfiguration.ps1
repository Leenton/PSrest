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
        [bool]$StrictDepth,
        [Parameter(Mandatory=$false)]
        [swicth]$Force
    )
    
    $ErrorActionPreference = "Stop"

    try{
        $ConfigJson = Get-Content -Path "$($Global:AppData)/config.json" | ConvertFrom-Json
    }catch{
        Write-Warning "Unable to read config file. Either the config file does not exist or is not valid JSON."
        if ($Force -or $PSCmdlet.ShouldProcess("config.json", "Create a new config file")){
            /Users/leenton/python/PSrest/PSRest/Server/configuration/config.json
            Remove-Item -Path "$($Global:AppData)/config.json" -Force -ErrorAction SilentlyContinue
            Copy-Item -Path "$($Global:InstallPath)/configuration/DefaultConfig.json" -Destination "$($Global:AppData)/config.json" -Force
            $ConfigJson = Get-Content -Path "$($Global:AppData)/config.json" | ConvertFrom-Json
        }else{
            throw "Error: Unable to read config file, ensure that the config file exist and is valid JSON. Or use the -Force switch to create a new config file with default values and amend specified parameters."
        }
    }

    if ($Port){
        $ConfigJson.Port = $Port
    }

    if ($SSLCertificate){
        $ConfigJson.SSLCertificate = $SSLCertificate
    }

    if ($SSLKeyFile){
        $ConfigJson.SSLKeyFile = $SSLKeyFile
    }

    if ($SSLKeyFilePassword){
        $ConfigJson.SSLKeyFilePassword = $SSLKeyFilePassword
    }

    if ($SSLCiphers){
        $ConfigJson.SSLCiphers = $SSLCiphers
    }

    if ($DefaultTTL){
        $ConfigJson.DefaultTTL = $DefaultTTL
    }

    if ($MaxTTL){
        $ConfigJson.MaxTTL = $MaxTTL
    }

    if ($StrictTTL){
        $ConfigJson.StrictTTL = $StrictTTL
    }

    if ($ArbitraryCommands){
        $ConfigJson.ArbitraryCommands = $ArbitraryCommands
    }

    if ($Help){
        $ConfigJson.Help = $Help
    }

    if ($Docs){
        $ConfigJson.Docs = $Docs
    }

    if ($DefaultDepth){
        $ConfigJson.DefaultDepth = $DefaultDepth
    }

    if ($StrictDepth){
        $ConfigJson.StrictDepth = $StrictDepth
    }

    $ConfigJson | ConvertTo-Json | Set-Content -Path "$($Global:AppData)/config.json"

}