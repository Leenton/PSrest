function Get-PSRestConfiguration {
    [CmdletBinding()]
    param (
    )

    $ErrorActionPreference = 'Stop'

    try{
        $Configuration = [PSRestConfig]::new()
        $ConfigJson = Get-Content -Path "$($Global:AppData)/config.json" -Raw | ConvertFrom-Json
        $Keys = ($ConfigJson | Get-Member -MemberType NoteProperty).Name

        foreach ($Key in $Keys) {
            $Configuration.$Key = $ConfigJson.$Key
        }

        Write-Verbose "Configuration loaded from: $($Global:AppData)/config.json"
        
        return $Configuration
    }catch{
        throw "Error: Unable to read config file, ensure that the config file exists and is valid JSON."
    }   
}
