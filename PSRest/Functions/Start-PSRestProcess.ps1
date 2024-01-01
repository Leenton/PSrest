function Start-PSRestProcess {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$ProcessorId,
        [Parameter(Mandatory = $true)]
        [string]$Socket
    )

    process{
        Import-Module "$Global:DLLs/PSRestModule.dll"
        
        trap{
            if(!$command){
                #Process failed but no command was received, so it doesn't matter just exit
                exit 
            }

            #If we have a response try again, and if we fail again just exit
            try {
                Send-PSRestResponse -Ticket $command.Ticket -Socket $Socket -InputObject $Response
            }
            catch {
                exit
            }
        }
    
        while($true){
            #Get the command to execute
            $Command = Receive-PSRestCommand -Socket $Socket -ProcessorId $ProcessorId

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
            Send-PSRestResponse -Ticket $command.Ticket -Socket $Socket -InputObject $Response
            $Command = $null
        }
    }
}