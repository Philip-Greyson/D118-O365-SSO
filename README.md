
# # D118-O365-SSO

Scripts to sync the O365 Immutable IDs into Google account custom attributes which is needed for the O365 Single Sign In via Google accounts.

## Overview

This project is two scripts, one PowerShell and one Python that get the "Immutable IDs" from O365 for users and add them to custom attributes in their Google profile. The PowerShell portion needs to run first, and uses the MSOnline module to retrieve all users principalName (in our case this is the email), and Immutable ID which is exported to a .csv file. Then the Python script looks through all users in the organization and stores their current Immutable ID custom attribute in a dictionary for quick access, instead of needing to do a profile lookup for each user individually which saves a lot of time. Then the .csv file is read and users are iterated through, comparing the Immutable ID returned by PowerShell to what is currently in their Google profile. If there is a mismatch, an update is called on the Google profile to update the custom attribute to the correct value.

## Requirements

The following Environment Variables must be set on the machine running the script:

- MS_ENTRA_GRAPH_CLIENT_ID
- MS_ENTRA_GRAPH_TENANT_ID
- MS_ENTRA_GRAPH_CERTIFICATE_THUMBPRINT

These are fairly self explanatory, and just relate to the information of a Microsoft Entra registered application, created to use certificate based authentication. The client and tenant ID are found on the overview of the app inside of Entra, and the certificate thumbprint is on the certificates & secrets tab within the app after a certificate is uploaded.
Of course, this app is also required to have the proper API permissions, specifically Graph - User.Read.All.
The setup of the app is outside of the scope of this readme, but you can find decent guides online, [this](https://blog.admindroid.com/connect-to-microsoft-graph-powershell-using-certificate/) is one that I have used.

The following PowerShell module must be installed on the host machine:

- [Microsoft Graph](https://learn.microsoft.com/en-us/powershell/microsoftgraph/installation?view=graph-powershell-1.0)

____
The following Python library must be installed on the host machine (links to the installation guide):

- [Python-Google-API](https://github.com/googleapis/google-api-python-client#installation)

In addition, an OAuth credentials.json file must be in the same directory as the overall script. This is the credentials file you can download from the Google Cloud Developer Console under APIs & Services > Credentials > OAuth 2.0 Client IDs. Download the file and rename it to credentials.json. When the program runs for the first time, it will open a web browser and prompt you to sign into a Google account that has the permissions to disable, enable, deprovision, and move the devices. Based on this login it will generate a token.json file that is used for authorization. When the token expires it should auto-renew unless you end the authorization on the account or delete the credentials from the Google Cloud Developer Console. One credentials.json file can be shared across multiple similar scripts if desired.

There are full tutorials on getting these credentials from scratch available online. But as a quickstart, you will need to create a new project in the Google Cloud Developer Console, and follow [these](https://developers.google.com/workspace/guides/create-credentials#desktop-app) instructions to get the OAuth credentials, and then enable APIs in the project (the Admin SDK API is used in this project).
____

Finally, in Google Admin, you must create a custom attribute to store the Immutable ID. This can be done from Directory > Users > More Options > Manage Custom Attributes. You can create a new category or use an existing one if you have other custom attributes, and then the Immutable ID attribute needs to be a text field.

Take the names of the category and field name and set the `CUSTOM_ATTRIBUTE_CATEGORY` and `CUSTOM_ATTRIBUTE_NAME` constants in the Python script to match them.

If there are spaces, or you made an attribute, deleted it and then made a new one with the same name, the names can sometimes not match what they are actually called internally in Google. To see all the custom attributes for a user, you can use `print( user.get('customSchemas', {}))` inside a user query that includes `projection = full` and it will show all their custom attribute category and field names, which you can then use to plug into the constants.

## Customization

The script is pretty simple and should not need much customization, besides making sure `CUSTOM_ATTRIBUTE_CATEGORY` and `CUSTOM_ATTRIBUTE_NAME` are correct.

- If you want to change the name of the .csv file that is used, you will have to edit `$OutputFileName` in the PowerShell script and `INPUT_FILE_NAME` in the Python script.
