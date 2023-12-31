$client = @{client_id='36c9adc3-f9da-4170-b087-a3eaa14e14b3'; client_secret='1c051bd3-ec5d-479c-b777-60e5e92cbf5a'; grant_type="client_credential";}
$token = Invoke-WebRequest -Uri http://localhost/oauth -Method POST -Body $client 
$header = @{Authorization = "Bearer $(($token.content | ConvertFrom-Json).accesstoken)"}

Invoke-WebRequest -Method Post -Headers $header -Uri http://localhost/run -Body (@{cmdlet="Write-Host"} | convertto-json)  -ContentType application/json