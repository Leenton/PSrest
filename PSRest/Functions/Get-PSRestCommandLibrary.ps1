function Get-PSRestCommandLibrary{

    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Enabled,

        [Parameter(Mandatory=$true)]
        [string]$Separator,

        [switch]$AsBase64
    )

    $ErrorActionPreference = 'Stop'

    $Enabled = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Enabled))
    $EnabledCmdlets = ConvertFrom-Json -InputObject $Enabled
    $Commands = @()
    
    # Add the commands that are in the enabled list
    $EnabledCmdlets | ForEach-Object {
        $Commands += Get-Command -Name $_ 
    }

    #Get only the unique commands in the Commands array so we don't reprocess data
    $Commands = $Commands | Sort-Object -Property Name -Unique
    
    #Get the help file for each command
    $Commands = foreach($Command in $Commands){
        try{
            $Help = Get-Help -Name $Command.Name -Full 
            $Mandatory = if($Help.Parameters.Parameter | Where-Object {
                $_.Required -eq $true
            }){
                $true
            }else{
                $false
            }

            @{
                Name = $Command.Name
                MandatoryParameters = $Mandatory
                Module = $Command.Source
                Version = $Command.Version
                Help = $Help | Out-String
            }
        }catch{
            continue
        }
    }
    
    if($Commands.count -gt 1){
        $Commands =  ConvertTo-Json -InputObject $Commands
    }elseif($Commands.count -eq 1){
        $Commands = ConvertTo-Json -InputObject @($Commands)
    }else{
        $Commands = ConvertTo-Json -InputObject @()
    }
    
    if ($AsBase64){
        Write-host "$Seperator$([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Commands)))"
    }
    else{
        Write-host $Commands
    }

}