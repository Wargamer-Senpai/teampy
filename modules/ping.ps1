
$pingResult = ping -n 1 $args[0]
$latency = $pingResult | Select-String "ms" | ForEach-Object { $_.ToString().Split(' ')[6] } 
$latency = $latency
Write-Output "$latency".Replace(",", "")