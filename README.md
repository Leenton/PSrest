# PSrest

You can run the application by importing the PSRest module and running the Start-PSRestServer command. 

```powershell
Import-Module .\PSRest.psm1
Start-PSRestServer
```

## Configuration

The application can be configured by editing the config.ini file or by using the Set-PSRestConfig command. 

```powershell
Set-PSRestConfig -PSModules PSRest -DisabledCommands Remove-Item -EnabledCommands Get-Process
```

```powershell
Enable-PSRestCommand -Command Get-Process -Disabled
```

```powershell
Disable-PSRestCommand -Command Get-Process
```

```powershell
Add-PSRestModule -Module ActiveDirectory
```

```powershell
Remove-PSRestModule -Module ActiveDirectory
```

```powershell
Get-PSRestConfig
```

## User Management


Overall plan, we will go heard for like 2 or 3 hours and speed implement our idea.


WHat is the idea, make a HTTP endpoint for powershell. basic idea is in your config file you define things like, what your PS repository is

How often you want to check for updates from the PSRepo,

Which powershell modules do you want to expose to the applications. 

Which commands are forbidden. 


What is the problem with the async, just load a new powershell session each time you wann do something? 


Well powershell is fucking SLOW


SLOOOOOOWWWWWW

And python is also FUCKING SLOW SLOOOOOOOW


it takes a quatrer of a second to run a command on my pc, A QUATER of a second! 



Why not make everything into a powershell JOB? 

What are the issues that can arise from doing everything in JOBS? 

NO PS profile, 

NO have to reload the module each time we run a command. 

Jobs are better since we don'ty have to 