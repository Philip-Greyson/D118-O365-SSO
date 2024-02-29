$OutputFileName = "Immutable-Ids.csv"  # Name of the output file
$OutputPath= Join-Path $PSScriptRoot $OutputFileName  # Construct the output path string by taking the current directory and appending the output file name

# Office 365 Credentials
$O365UserName = $Env:O365_USERNAME  # Get the O365 username from the environment variable
$O365Password = $Env:O365_PASSWORD | ConvertTo-SecureString -AsPlainText -Force  # Get the 065 password from the environment variable, convert it from plaintext to securestring
$O365Credentials = New-Object System.Management.Automation.PSCredential ($O365UserName, $O365Password)  # Create the O365 credentials object
Connect-MsolService -Credential $O365Credentials  # Connect to o365/Azure AD - whatever they want to call it now
# Do the export
Get-MsolUser -All | Select-Object UserprincipalName, ImmutableID | Export-Csv $OutputPath  # Export the UPN and immutible ID fields for all users and export them to our output path
