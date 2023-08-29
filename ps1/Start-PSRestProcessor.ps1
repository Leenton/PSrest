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
        
    }

    process{
        import-Module '/Users/leenton/c#/PSRestModule/PSRestModule/bin/Debug/net7.0/PSRestModule.dll'
        
        trap{
            if(!$command){
                #Process failed but no command was received, so it doesn't matter just exit
                exit 
            }

            #If we have a response try again, and if we fail again just exit
            try {
                Send-PSRestResponse -Ticket $command.Ticket -ResponseDirectory $ResponseDirectory -InputObject $Response -WaitTime $WaitTime
            }
            catch {
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