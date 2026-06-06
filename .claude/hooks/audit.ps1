$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$hook = $env:HOOK_EVENT
$input = $input | Out-String
Add-Content -Path ".claude\audit.jsonl" -Value "{`"ts`":`"$ts`",`"hook`":`"$hook`",`"tool`":`"detected`"}"
