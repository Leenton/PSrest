function Format-Command ($Command){
    $FormatedCommand = @{}
    $RawComand = Get-Command $Command -ShowCommandInfo
    
    try{
        $Aliases = Get-Alias -Definition $Command
    }catch{
        $Aliases = $Null
    }
    
    $FormatedCommand['Names'] = @($RawComand.Name)
    if($Alias){
        foreach($Alias in $Aliases){
            $FormatedCommand['Names'] += $Alias
        }
    }

    foreach($ParameterSet in $RawComand.ParameterSets){
        $FormatedCommand['ParameterSets'] += Format-ParameterSet $ParameterSet
    }

    #check for common parameters on the command if they exist call the function to get the help for them
    if((Get-Help $Command).CommonParameters){
        $FormatedCommand['CommonParameters'] = Get-CommonParameters
    }else{
        $FormatedCommand['CommonParameters'] = @()
    }

    return $FormatedCommand
}

function Format-ParameterSet($ParameterSet){
    $FormatedParameterSet = @{}
    $FormatedParameterSet['Name'] = $ParameterSet.Name
    $FormatedParameterSet['Parameters'] = $ParameterSet.Parameters
    return $FormatedParameterSet
}

function Get-CommonParameters(){
    #return the standard common parameters and their data types
    $CommonParameters = @{
        'Verbose' = 'SwitchParameter'
        'Debug' = 'SwitchParameter'
        'ErrorAction' = 'ActionPreference'
        'ErrorVariable' = $null
        'WarningAction' = 'ActionPreference'
        'WarningVariable' = $null
        'InformationAction' = 'ActionPreference'
        'InformationVariable' = $null
        'OutVariable' = $null
        'OutBuffer' = $null
        'PipelineVariable' = $null
        'WhatIf' = 'SwitchParameter'
        'Confirm' = 'SwitchParameter'
    }
    return $CommonParameters
}

function Get-PSRestCommands($Module, $DissabledCommands){
    try {
        $Commands = Get-Command -Module $Module | Where-Object{$_ -notin $DissabledCommands}
        $CommandFormats = @()
        foreach($Command in $Commands){
            $CommandFormats += Format-Command $Command
        }
    }
    catch {
        throw $_
    }
    
    return $CommandFormats
}
