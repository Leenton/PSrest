function Start-PSRestProcessor($ProcessID,$PublicKey, $ProcessorQueue, $ResponseQueue){
    $ErrorActionPreference = "Continue"
    while($true){
        #Get the command from the queue and execute it
        try{
            $Result = Invoke-PSRestCommand -Command (Get-PSRestCommand -ProcessorQueue $ProcessorQueue)
        }
        catch{
            $Result = $_
        }

        Save-PSRestCommandResult -Result $Result -ResponseQueue $ResponseQueue -ProcessID $ProcessID
    }
} 
