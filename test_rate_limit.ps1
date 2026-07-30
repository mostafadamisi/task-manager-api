$base = "http://127.0.0.1:8000"

Write-Host "=== Quick Endpoint Tests ==="

try {
    $r = Invoke-WebRequest -Uri "$base/health" -UseBasicParsing
    Write-Host ("Health: " + $r.StatusCode)
} catch { Write-Host ("Health: " + $_.Exception.Response.StatusCode.value__) }

try {
    $r = Invoke-WebRequest -Uri "$base/projects/" -UseBasicParsing
    Write-Host ("List projects: " + $r.StatusCode)
} catch { Write-Host ("List projects: " + $_.Exception.Response.StatusCode.value__) }

try {
    $r = Invoke-WebRequest -Uri "$base/tasks/" -UseBasicParsing
    Write-Host ("List tasks: " + $r.StatusCode)
} catch { Write-Host ("List tasks: " + $_.Exception.Response.StatusCode.value__) }

try {
    $r = Invoke-WebRequest -Uri "$base/tasks/000000000000000000000000" -UseBasicParsing
    Write-Host ("Task 404: " + $r.StatusCode)
} catch { Write-Host ("Task 404: " + $_.Exception.Response.StatusCode.value__) }

Write-Host "`n=== Rate Limit Test ==="

$headers = @{"Content-Type" = "application/json"}
for ($i = 0; $i -lt 10; $i++) {
    $body = '{"name":"User' + $i + '","email":"user' + $i + '@test.com","password":"pass123"}'
    try {
        $r = Invoke-WebRequest -Uri "$base/auth/register" -Method POST -Body $body -Headers $headers -UseBasicParsing
        Write-Host ("Register " + $i + ": " + $r.StatusCode)
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        Write-Host ("Register " + $i + ": " + $code)
    }
}

Write-Host "`nDone!"
