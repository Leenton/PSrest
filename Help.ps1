function Format-Help ($command){
    $Help = {}
    $RawHelp = Get-Help $Command
    
    #add the command name, and the alias to an array of names
    $Help['Names'] = @($Command.Name)

    #add the command name, and the alias to an array of names
    $Help['Aliases'] = @($Command.Alias)

    #check for common parameters on the command if they exist call the function to get the help for them
    if($RawHelp.CommonParameters){
        foreach ($CommonParameter in Get-CommonParameters){
            $Help['Parameters'] += $CommonParameter
        }
    }

    foreach($Parameter in $RawHelp.Parameters){
        $Help['Parameters'] += $Parameter
    }

    return $Help
}
function get-commands($Module, $DissabledCommands){
    try {
        $Commands = Get-Command -Module $Module | Where-Object{$_ -notin $DissabledCommands}
        $CommandHelp = @()
        foreach($Command in $Commands){
            $CommandHelp += Format-Help $Command
        }


    }
    catch {
        {1:<#Do this if a terminating exception happens#>}
    }
    get-module $module
}

function Get-CommonParameters(){
    #return the standard common parameters and their data types
    $CommonParameters = @(
        'Verbose',
        'Debug',
        'ErrorAction',
        'ErrorVariable',
        'WarningAction',
        'WarningVariable',
        'InformationAction',
        'InformationVariable',
        'OutVariable',
        'OutBuffer',
        'PipelineVariable',
        'WhatIf',
        'Confirm'
    )
}


