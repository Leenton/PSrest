function Get-PSRestActions{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$True)]
        [string]$Filter,
        [Parameter(Mandatory=$True)]
        [string]$Separator,
        [switch]$AsBase64
    )

    $Filter = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Filter))
    $EnabledCommand, $EnabledModule, $DisabledModuleCommand = $Filter.Split($Separator)

    # Verify that the cmdlets exist on the system.
    $Cmdlets = @()

    if ($EnabledCommand -eq '*'){
        $Cmdlets = Get-Command | Select-Object -ExpandProperty Name
    }elseif ($EnabledCommand -ne '') {
        $EnabledCommand = $EnabledCommand.Split(',')
    
        $EnabledCommand | ForEach-Object {
            $Command = Get-Command $_ -ErrorAction SilentlyContinue
            if ($Command){
                $Cmdlets += $Command.Name
            }else{
                throw "The cmdlet '$_' does not exist on the system."
            }
        }
    }

    if ($EnabledModule -ne ''){
        # Verify that the modules exist on the system.
        $EnabledModule | ForEach-Object {
            $Module = Get-Module $_ -ErrorAction SilentlyContinue -ListAvailable
            if ($Module){
                $Module.ExportedCmdlets.GetEnumerator() | ForEach-Object {
                    $Cmdlets += $_.Key
                }
            }else{
                throw "The module '$_' does not exist on the system."
            }
        }
    }

    if ($DisabledModuleCommand -ne ''){
        # Remove any cmdlets that are disabled.
        $DisabledModuleCommand | ForEach-Object {
            $Command = Get-Command $_ -ErrorAction SilentlyContinue
            if ($Command){
                $Cmdlets = $Cmdlets | Where-Object { $_ -ne $Command.Name }
            }else{
                throw "The cmdlet '$_' does not exist on the system."
            }
        }
    }

    if ($AsBase64){
        $Cmdlets = $Cmdlets | ConvertTo-Json -Compress
        $Cmdlets = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Cmdlets))
    }

    return $Cmdlets
}