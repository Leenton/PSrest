function Get-PSRestCommandLibrary{

    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        # The modules to get the commands from
        [string[]]$Module,
        [Parameter(Mandatory=$false)]
        # The commands that are not in the specified modules which should be included in the library
        [string[]]$EnabledCommands,
        [Parameter(Mandatory=$false)]
        # The commands that are in the specified modules which should be excluded from the library
        [string[]]$DisabledCommands,

        [Parameter(Mandatory=$true)]
        # The string to use to prepened to the returned base64 output for capture. 
        [string]$Seperator
    )

    process{

        $Commands = @()

        if($Module -eq '*'){
            $ModuleCommands = Get-Command
        }else{
            foreach($Mod in $Module){
                $ModuleCommands += Get-Command -Module $Mod
            }
        }
        
        # Remove the commands that are in the disabled list
        foreach($Command in $ModuleCommands){
            if($DisabledCommands -notcontains $Command.Name){
                $Commands += $Command
            }
        }

        # Add the commands that are in the enabled list
        foreach($Command in $EnabledCommands){
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
            $Commands =  $Commands | ConvertTo-Json
        }elseif($Commands.count -eq 1){
            $Commands =  @($Commands) | ConvertTo-Json
        }else{
            $Commands =  @() | ConvertTo-Json
        }
        
        Write-host "$Seperator$([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Commands)))"
    }
}

function Get-WaitForRandom{
    $Wait = Get-Random -Minimum 1 -Maximum 13
    Write-Host "Waiting for $Wait seconds"
    Start-Sleep -Seconds $Wait
    return $Wait
}

function Start-PSRestProcessor {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$ProcessorId,
        [Parameter(Mandatory = $true)]
        [string]$SocketPath,
        [Parameter(Mandatory = $true)]
        [string]$ResponseDirectory,
        [Parameter(Mandatory = $true)]
        [int]$WaitTime = 250
    )

    begin{
        import-Module '/Users/leenton/c#/PSRestModule/PSRestModule/bin/Debug/net7.0/PSRestModule.dll'
    }

    process{
        trap{
            if(!$command){
                #Process failed but no command was received, so it doesn't matter just exit
                exit
            }
        }
    
        while($true){
            #Get the command to execute
            $Command = Receive-PSRestCommand -SocketPath $SocketPath -ProcessorId $ProcessorId

            #Try and execute the command and send the result back
            try{
                $Data = Invoke-Expression -Command $Command 
            }
            catch {
                $Exception = $_.Exception.Message
            }

            #Convert the data to json
            $Response = @{
                data = $Data;
                error = $Exception
            } | ConvertTo-Json -Depth $command.Depth

            #Send the response over the wire
            Send-PSRestResponse -Ticket $command.Ticket -ResponseDirectory $ResponseDirectory -InputObject $Response -WaitTime $WaitTime
            $Command = $null
        }
    }
}