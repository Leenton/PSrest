function Add-Application  {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        [ValidateSet('client_credential', 'access_token')]
        [string]$Authentication = 'client_credential',
        [Parameter(Mandatory=$false)]
        [string[]]$EnabledCommand,
        [Parameter(Mandatory=$false)]
        [string[]]$EnabledModule,
        [Parameter(Mandatory=$false)]
        [string[]]$DisabledModuleCommand
    )

    # Verify that the cmdlets exist on the system.
    $Cmdlets = @()
    $EnabledCommand | ForEach-Object {
        $command = Get-Command $_ -ErrorAction SilentlyContinue
        if ($command){
            $Cmdlets += $_
        }else{
            throw "The cmdlet '$_' does not exist on the system."
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

    $Cmdlets
}