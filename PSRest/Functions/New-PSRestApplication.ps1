function New-PSRestApplication()
{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        # The name of the application
        [string]$Name,
        # The description of the application
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        # The type of authentication to use, either 'client_credential' or 'access_token'. Note that 'access_token' is not recommended for security reasons.
        [ValidateSet('client_credential', 'access_token')]
        [string]$Authentication = 'client_credential',
        [Parameter(Mandatory=$false)]
        # The cmdlets the application is permitted to use.
        [string[]]$EnabledCommand = @(),
        [Parameter(Mandatory=$false)]
        # The modules the application is permitted to use.
        [string[]]$EnabledModule = @(),
        [Parameter(Mandatory=$false)]
        # The cmdlets the application is not permitted to use.
        [string[]]$DisabledModuleCommand = @()
    )

    #Check that the description is no more than 10^9 bytes long when encoded as UTF-8
    if ($Description){
        $DescriptionBytes = [System.Text.Encoding]::UTF8.GetBytes($Description)
        if ($DescriptionBytes.Length -gt 1000000000){
            throw "The description is too long. The description must be no more than 10^9 bytes long when encoded as UTF-8."
        }
    }

    # Verify that the cmdlets exist on the system.
    $Cmdlets = @()

    if ($EnabledCommand -eq '*'){
        $Cmdlets = Get-Command | Select-Object -ExpandProperty Name
    }else{
        $EnabledCommand | ForEach-Object {
            $command = Get-Command $_ -ErrorAction SilentlyContinue
            if ($command){
                $Cmdlets += $_
            }else{
                throw "The cmdlet '$_' does not exist on the system."
            }
        }
    }

    # Verify that the modules exist on the system.

    $EnabledModule | ForEach-Object {
        $Module = Get-Module $_ -ErrorAction SilentlyContinue
        if ($Module){
            $Module.ExportedCmdlets.GetEnumerator() | ForEach-Object {
                $Cmdlets += $_.Key
            }
        }else{
            throw "The module '$_' does not exist on the system."
        }
    }

    # Remove any cmdlets that are disabled.
    $DisabledModuleCommand | ForEach-Object {
        $command = Get-Command $_ -ErrorAction SilentlyContinue
        if ($command){
            $Cmdlets = $Cmdlets | Where-Object { $_ -ne $command }
        }else{
            throw "The cmdlet '$_' does not exist on the system."
        }
    }

    Write-Verbose "The following cmdlets will be enabled for the application: $($Cmdlets -join ',')"

    # Verify that the application does not already exist.
    $existingApplication = Get-PSRestApplication -Name $Name -ErrorAction SilentlyContinue
    if ($existingApplication){
        throw "The application '$Name' already exists."
    }

    $result = Invoke-PSRestConsole -command  "--method add --name '$Name' --description '$Description' --authentication '$Authentication' --enabledActions '$($EnabledCommand -join ',')' --enabledModules '$($EnabledModule -join ',')' --disabledActions '$($DisabledModuleCommand -join ',')'"
    
    try{
        $application = ConvertFrom-Json $result
        return $application.data
    }catch{
        throw "Error occured attempting to add the specified application."
    }
}