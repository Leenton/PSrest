$Global:AppData = ((&python3  ./ConsoleApp.py --method config) | convertfrom-json).data

class PSRestConfig{
    [string]$Hostname;
    [int]$Port;
    [string]$Cert;
    [string]$Repository;
    [int]$DefaultTTL;
    [int]$MaxTTL;
    [bool]$ArbitraryCommands;
    [string[]]$Modules;
    [string[]]$Enabled;
    [string[]]$Disabled;
    [bool]$Help;
    [int]$DefaultDepth;
}

function Get-PSRestConfig {
    [CmdletBinding()]
    param (
    )

    $Config = [PSRestConfig]::new()

    $ConfigJson = Get-Content -Path "$($Global:AppData.Path)/config.json" | ConvertFrom-Json

    try{
        $Config | Get-Member -MemberType Property | ForEach-Object {
            if($ConfigJson."$($_.Name)" -eq 'Modules'){
                
                if($ConfigJson."$($_.Name)" -contains '*' -and $ConfigJson."$($_.Name)".Count -eq 1){
                    $collection = $ConfigJson."$($_.Name)"
                    foreach ($ in $collection) {
                        <# $ is the current item #>
                    }
                    throw "Error: Unable to read config file, ensure that the config file exists and is valid JSON."
                }
            }

            $Config."$($_.Name)" = $ConfigJson."$($_.Name)"
        }
    }catch{
        throw "Error: Unable to read config file, ensure that the config file exists and is valid JSON."
    }

    return $Config
}



function Set-PSRestConfig {
    param (
        OptionalParameters
    )
    
}

function Enable-PSRestCommand {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [switch]$Disabled
    )
    
}

function Disable-PSRestCommand {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Command
    )
    
}

function Add-PSRestModule {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Module
    )
    
}

function Remove-PSRestModule {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Module
    )
    
}


