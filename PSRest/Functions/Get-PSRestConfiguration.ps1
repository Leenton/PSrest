function Get-PSRestConfig {
    [CmdletBinding()]
    param (
    )

    $Configuration = [PSRestConfig]::new()

    $ConfigJson = Get-Content -Path "$($Global:AppData.Path)/config.json" | ConvertFrom-Json

    # try{
    #     $Config | Get-Member -MemberType Property | ForEach-Object {
    #         if($ConfigJson."$($_.Name)" -eq 'Modules'){
                
    #             if($ConfigJson."$($_.Name)" -contains '*' -and $ConfigJson."$($_.Name)".Count -eq 1){
    #                 $collection = $ConfigJson."$($_.Name)"
    #                 foreach ($ in $collection) {
    #                     <# $ is the current item #>
    #                 }
    #                 throw "Error: Unable to read config file, ensure that the config file exists and is valid JSON."
    #             }
    #         }

    #         $Config."$($_.Name)" = $ConfigJson."$($_.Name)"
    #     }
    # }catch{
    #     throw "Error: Unable to read config file, ensure that the config file exists and is valid JSON."
    # }

    return $Config
}
