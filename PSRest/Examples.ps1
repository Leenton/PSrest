$client = @{client_id='2a3936cf-4064-49db-bec1-6246434ac246'; client_secret='e5d4651f-d5f2-4cb3-8172-d0a008e3f73b'; grant_type="client_credential";}
$token = Invoke-WebRequest -Uri http://localhost/oauth -Method POST -Body $client 
$header = @{Authorization = "Bearer $(($token.content | ConvertFrom-Json).access_token)"}

Invoke-WebRequest -Method Post -Headers $header -Uri http://localhost/run -Body (@{cmdlet="Write-Host"} | convertto-json)  -ContentType application/json





$client = @{client_id='2a3936cf-4064-49db-bec1-6246434ac246'; client_secret='e5d4651f-d5f2-4cb3-8172-d0a008e3f73b'; grant_type="client_credential";}
$token = Invoke-WebRequest -Uri http://10.10.10.12:5005/oauth -Method POST -Body $client 
$header = @{Authorization = "Bearer $(($token.content | ConvertFrom-Json).access_token)"}

Invoke-WebRequest -Method Post -Headers $header -Uri http://10.10.10.12:5005/run -Body (@{cmdlet="Write-Host"} | convertto-json)  -ContentType application/json