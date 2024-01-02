class PSRestConfig{
    [int]$Port;
    [string]$SSLCertificate;
    [string]$SSLKeyFile;
    [string]$SSLKeyFilePassword;
    [string]$SSLCiphers;
    [int]$DefaultTTL;
    [int]$MaxTTL;
    [bool]$StrictTTL;
    [bool]$ArbitraryCommands;
    [bool]$Help;
    [bool]$Docs;
    [int]$DefaultDepth;
    [bool]$StrictDepth;
}