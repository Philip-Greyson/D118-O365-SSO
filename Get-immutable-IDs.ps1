$OutputFileName = "Immutable-Ids.csv"
$OutputPath= Join-Path $PSScriptRoot $OUTPUT_FILE_NAME

# Office 365 Credentials
$O365UserName = $Env:O365_USERNAME
$0365Password = $Env:O365_PASSWORD | ConvertTo-SecureString
#$O365Password = Get-Content C:\D118-O365-SSO\O365-Pass.txt | ConvertTo-SecureString
$O365Credentials = New-Object System.Management.Automation.PSCredential ($O365UserName, $O365Password)
Connect-MsolService -Credential $O365Credentials
# Do the export
$exportUsers = Get-MsolUser -All | Select-Object UserprincipalName, ImmutableID | Export-Csv $OutputPath
