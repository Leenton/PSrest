$Global:InstallPath = "$PSScriptRoot/Server"
$Global:DLLs = "$PSScriptRoot/DLLs"
$Global:AppData = ''

if ($PSVersionTable.Platform -eq 'Win32NT') {
    $Global:Python = "python.exe"
} else {
    $Global:Python = "python3"
}

# dot source the functions
foreach($file in Get-ChildItem -Path "$PSScriptRoot/Functions" -Filter *.ps1){
    . $file.FullName
}

#Check the config file to know if check for updates is enabled
$Global:CheckForUpdates = $true

$about = (Invoke-PSRestConsole -command "--method config" | ConvertFrom-Json).data
$Global:AppData = $about.path
$GLobal:Platform = $about.platform
$Global:Config = Get-PSRestConfig 