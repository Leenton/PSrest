function Invoke-PSRestConsole(){
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        # Run the specified command in the consol and return the result.
        [string]$Command
    )

    $ErrorActionPreference = 'Stop'

    try{
        Enter-PSRestVirtualEnvironment
    }catch{
        throw "Unable to enter virtual environment to run the command requested. Contact PSRest support for assistance."
    }

    $FullCommand = "& $($Global:Python) $($Global:InstallPath + '/' + "ConsoleApp.py") " + $Command
    $result = Invoke-Expression -Command ($FullCommand)

    Exit-PSRestVirtualEnvironment

    return $result
}
