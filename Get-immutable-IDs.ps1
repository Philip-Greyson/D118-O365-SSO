$OutputFileName = "Immutable-Ids.csv"  # Name of the output file
$OutputPath= Join-Path $PSScriptRoot $OutputFileName  # Construct the output path string by taking the current directory and appending the output file name

# Entra Credentials for our app
$EntraAppClientID = $Env:MS_ENTRA_GRAPH_CLIENT_ID  # get the client ID from the environment variable
$EntraAppTenantID = $Env:MS_ENTRA_GRAPH_TENANT_ID  # get the tenant ID from the environment variable
$EntraAppCertThumbprint = $Env:MS_ENTRA_GRAPH_CERTIFICATE_THUMBPRINT  # get the app certificate thumbprint from the environement variable

Connect-MgGraph -ClientID $EntraAppClientID -TenantID $EntraAppTenantID -CertificateThumbprint $EntraAppCertThumbprint -NoWelcome  # make the connection via MS Graph
# do the export. Use the Get-MgUser to find all users, specfiy that it needs to include the UPN and immutableid
Get-MgUser -All -Select "UserPrincipalName, OnPremisesImmutableID" | Select-Object UserPrincipalName,OnPremisesImmutableID | Export-Csv $OutputPath  # using the select-object to filter the output to just the two fields, then export to our output path