function Invoke-PSRestConsole(){
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        # Run the specified command in the consol and return the result.
        [string]$Command
    )

    $ErrorActionPreference = 'Stop'

    $FullCommand = "& $($Global:Python) $($Global:InstallPath + '/' + "ConsoleApp.py") " + $Command
    $result = Invoke-Expression -Command ($FullCommand)

    return $result
}
