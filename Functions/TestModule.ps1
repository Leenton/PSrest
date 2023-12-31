function Import-PSRest {
    #Copy this /Users/leenton/python/PSrest/PSRest to $env:PSModulePath

    Remove-Item -Path "$($env:PSModulePath.Split(":")[0])/PSRest" -Recurse -Force -ErrorAction SilentlyContinue

    Copy-Item -Path "/Users/leenton/python/PSrest/PSRest" -Destination "$($env:PSModulePath.Split(":")[0])/PSRest" -Recurse -Force
    Import-Module -Name "$($env:PSModulePath.Split(":")[0])/PSRest/PSRest.psd1"
}
    