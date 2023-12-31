$Global:InstallPath = "$PSScriptRoot/Server"
$Global:DLLs = "$PSScriptRoot/DLLs"
$Global:AppData = ''

# dot source the functions
foreach($file in Get-ChildItem -Path "$PSScriptRoot/Functions" -Filter *.ps1){
    . $file.FullName
}

#Check the config file to know if check for updates is enabled
$Global:CheckForUpdates = $true


$Global:AppData = (Invoke-PSRestConsole -command "--method config" | ConvertFrom-Json).path
$Global:Config = Get-PSRestConfig 