$Global:InstallPath = '/Users/leenton/python/PSrest'
$Global:CheckForUpdates = $true

# dot source the functions
foreach($file in Get-ChildItem -Path "$PSScriptRoot/Functions" -Filter *.ps1){
    . $file.FullName
}