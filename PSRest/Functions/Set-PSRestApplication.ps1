function Set-PSRestApplication()
{
    [CmdletBinding(DefaultParameterSetName='Id')]
    param
    (
        [Parameter(Mandatory=$true, ParameterSetName='Name', Position=0)]
        # The name of the application
        [string]$Name,
        [Parameter(Mandatory=$true, ParameterSetName='Id', Position=0)]
        # The name of the application
        [string]$Id,
        # The description of the application
        [Parameter(Mandatory=$false)]
        [string]$Description,
        [Parameter(Mandatory=$false)]
        # The cmdlets the application is permitted to use.
        [string[]]$EnabledCmdlets,
        [Parameter(Mandatory=$false)]
        # The modules the application is permitted to use.
        [string[]]$EnabledModules,
        [Parameter(Mandatory=$false)]
        # The cmdlets the application is not permitted to use.
        [string[]]$DisabledModuleCmdlets
    )

    $ErrorActionPreference = 'Stop'

    try{
        if($Name){
            $application = Get-PSRestApplication -Name $Name -ErrorAction SilentlyContinue
            if(!$application){
                throw "The application '$Name' does not exist."
            }
            $Id = $application.id
        }else{
            $application = Get-PSRestApplication -Id $Id -ErrorAction SilentlyContinue
            if(!$application){
                throw "The application with id '$Id' does not exist."
            }
        }

        # Check that the description is no more than 10^9 bytes long when encoded as UTF-8
        if ($Description)
        {
            $DescriptionBytes = [System.Text.Encoding]::UTF8.GetBytes($Description)
            if ($DescriptionBytes.Length -gt 1000000000)
            {
                throw "The description is too long. The description must be no more than 10^9 bytes long when encoded as UTF-8."
            }
        }

        # Verify that the cmdlets exist on the system.
        $Cmdlets = @()

        if($null -ne $EnabledCmdlets){
            if ($EnabledCmdlets -eq '*'){
                $Cmdlets = Get-Command | Select-Object -ExpandProperty Name
            }else{
                $EnabledCmdlets | ForEach-Object {
                    $command = Get-Command $_ -ErrorAction SilentlyContinue
                    if ($command){
                        $Cmdlets += $_
                    }else{
                        throw "The cmdlet '$_' does not exist on the system."
                    }
                }
            }
        }

        # Verify that the modules exist on the system.
        if($null -ne $EnabledModules){
            $EnabledModules | ForEach-Object {
                $Module = Get-Module $_ -ErrorAction SilentlyContinue
                if ($Module){
                    $Module.ExportedCmdlets.GetEnumerator() | ForEach-Object {
                        $Cmdlets += $_.Key
                    }
                }else{
                    throw "The module '$_' does not exist on the system."
                }
            }
        }

        # Remove any cmdlets that are disabled.
        if($null -ne $DisabledModuleCmdlets){
            $DisabledModuleCmdlets | ForEach-Object {
                $command = Get-Command $_ -ErrorAction SilentlyContinue
                if ($command){
                    $Cmdlets = $Cmdlets | Where-Object { $_ -ne $command }
                }else{
                    throw "The cmdlet '$_' does not exist on the system."
                }
            }
        }

        $application = Invoke-PSRestConsole -command (
            "--method set " +
            "--id $Id $($Description ? "--description '$Description' " : '')" +
            "$($EnabledCmdlets ? "--enabledActions '$($EnabledCmdlets -join ',')' " : '')" +
            "$($EnabledModules ? "--enabledModules '$($EnabledModules -join ',')' " : '')" +
            "$($DisabledModuleCmdlets ? "--disabledActions '$($DisabledModuleCmdlets -join ',')' " : '' )"
        ) | ConvertFrom-Json

        if($application.data -eq $true){
            return
        }else{
            throw "Error occured attempting to modify the specified application."
        }
    }catch{
        throw "Error occured attempting to modify the specified application."
    }
}