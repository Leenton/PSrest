function Enter-PSRestVirtualEnvironment{

    Install-PSRestDependencies

    ."$($Global:Dependencies)/bin/Activate.ps1"
}