# PSrest

PSrest is a PowerShell module that provides a RESTful HTTP endpoint for executing PowerShell commands and scripts. The module allows you to expose PowerShell functionality as a web service, making it easy to integrate PowerShell with other applications and services.

## Getting Started

To get started with PSrest, import the PSRest module and run the Start-PSRestServer command:

```powershell
Import-Module .\PSRest.psm1
Start-PSRestServer
```

This will start the PSrest server and expose a RESTful HTTP endpoint at http://localhost:8080
You can change the port by editing the config.yaml file.

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
PSrest features basic user management functionality, allowing you to limit access commands executed by a given user. 

```powershell
Add-PSRestUser -Username admin -Password admin -Enabled
```

```powershell
Remove-PSRestUser -Username admin
```

```powershell
Enable-PSRestUser -Username admin
```

```powershell
Disable-PSRestUser -Username admin
```


## TODO relic
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


## Reasons why events and procsses tab where dropped:

The additional development time and effort needed to bring these features to
fruition were too large to be handled in the intial release of PSRest without
significantly increasing the planned development time for this project.

A slimer less feature rich version of this project is inline with the original
problem statement this project was aiming to resolve. If the GUI features removed
are paramount for your usecase, this project is not ideal for your usecase, and
I recomend swithing to Powershell Universal by IronMan Software which offers a far
richer GUI and more mature platform for taking this type of problem. 

