function Start-Server() {
    $server = Start-Process -FilePath $serverPath -ArgumentList $serverArgs -PassThru
    $server | Wait-Process
}

/
