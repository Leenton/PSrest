function Get-PSRestCommandLibrary{

    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        # The commands that are not in the specified modules which should be included in the library
        [string]$ConfigFile,

        [Parameter(Mandatory=$true)]
        # The string to use to prepened to the returned base64 output for capture. 
        [string]$Seperator
    )

    process{

        $Config = Get-Content -Path $ConfigFile | ConvertFrom-Json

        # Add the commands that are in the enabled list
        foreach($Command in $Config.Enabled){
            $Commands += Get-Command -Name $Command 
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
        
        Write-host "$Seperator$([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Commands)))"
    }
}