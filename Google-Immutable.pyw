"""Script to upload immutable IDs from file to custom attribute in Google Admin.

https://github.com/Philip-Greyson/D118-O365-SSO

Needs input from a .csv containing emails, immutable IDs generated from a PowerShell script.
Finds all users in domain, stores their current immutable ID in a dictionary.
Then goes through input file, comapres what ID should be to what it is currently.
If there is a mismatch, will update Google profile to be correct.

Needs the google-api-python-client, google-auth-httplib2 and the google-auth-oauthlib
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

# importing module
import os  # needed for environement variable reading
import os.path
from datetime import *
from typing import get_type_hints

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.group', 'https://www.googleapis.com/auth/admin.directory.group.member', 'https://www.googleapis.com/auth/apps.licensing']

INPUT_FILE_NAME = 'Immutable-Ids.csv'
CUSTOM_ATTRIBUTE_CATEGORY = "Office_365"
CUSTOM_ATTRIBUTE_NAME = "immutableID2"

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('admin', 'directory_v1', credentials=creds)

with open('ImmutableLog.txt', 'w') as log:
    with open(INPUT_FILE_NAME) as source:
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'Execution started at {startTime}')
        print(f'Execution started at {startTime}', file=log)

        # get all users in our domain and their immutable ID if they have one, stored into a dictionary for easier querying than one at a time api calls
        userDict = {}  # define dict that will contain sub-dict for each user containing their email and immutable id
        userToken = ''  # initialize blank userToken for use in looping query
        count = 1  # variable for counting which query we are on
        print('INFO: Finding all users in domain and their current immutable ID, this may take a while')
        print('INFO: Finding all users in domain and their current immutable ID, this may take a while', file=log)
        while userToken is not None:  # do a while loop while we still have a next page of results
            print(f'DBUG: Performing query loop #{count} for users and immutable IDs and storing them in users dict')  # have a simple output each loop so we can make sure its still running
            count += 1  # increment count
            userResults = service.users().list(customer='my_customer', orderBy='email', projection='full', pageToken=userToken).execute()  # return all users in our domain
            userToken = userResults.get('nextPageToken')
            users = userResults.get('users', [])
            for user in users:
                try:
                    # print(user)
                    # print(user, file=log)
                    email = user.get('primaryEmail', [])  # get their email
                    # print(user.get('customSchemas', {}).get('Office_365', {}), file=log)  # debug to see what fields are in this schema
                    currentImmutableID = user.get('customSchemas', {}).get(CUSTOM_ATTRIBUTE_CATEGORY, {}).get(CUSTOM_ATTRIBUTE_NAME, "")  # get the value currently in their immutable id field, return a blank dict at each time so that we dont error out if they have no values, empty string for final if it does not exist
                    if email is not None and currentImmutableID is not None:
                        # print(f'DBUG: Adding user to userDict - Email: {email} - Current ID: {currentImmutableID}')
                        # print(f'DBUG: Adding user to userDict - Email: {email} - Current ID: {currentImmutableID}', file=log)
                        userDict.update({email : currentImmutableID})  # add the email : id entry to the dict
                except Exception as er:
                    print(f'ERROR on user {user}: {er}')
                    print(f'ERROR on user {user}: {er}', file=log)

        # print(userDict, file=log)

        # go through each line in the input IDs file, check against their current id in their profile, and update the profile if neccessary
        lines = source.readlines()  # read all the lines of the immutable ids file and store them in a list
        for line in lines:
            try:
                if line[0] != '#':  # ignore lines that start with a pound sign
                    bodyDict = {}
                    line = line.strip()  # strip out new line characters, whitespace, etc
                    split = line.split(',')
                    user = split[0].strip('"').lower()  # strip out the double quotes, and convert to lowercase for better readability
                    immutableID = split[1].strip('"')  # strip out double quotes
                    # print(f'User: {user} - ID: {immutableID}')

                    currentImmutableID = userDict.get(user)
                    print(f'DBUG: User: {user} - ID: {immutableID} - Current: {currentImmutableID}')
                    print(f'DBUG: User: {user} - ID: {immutableID} - Current: {currentImmutableID}', file=log)
                    if immutableID != currentImmutableID:
                        if userDict.get(user, 'DNE') != 'DNE':  # check to see if the user exists in the userdict
                            print(f'INFO: User {user} needs ID updated from {currentImmutableID} to {immutableID}')
                            print(f'INFO: User {user} needs ID updated from {currentImmutableID} to {immutableID}', file=log)
                            bodyDict.update({'customSchemas' : {CUSTOM_ATTRIBUTE_CATEGORY : {CUSTOM_ATTRIBUTE_NAME : immutableID}}})
                            try:
                                # print(bodyDict)
                                # print(bodyDict, file=log)
                                outcome = service.users().update(userKey = user, body=bodyDict).execute()  # does the actual updating of the user profile
                                # print(outcome)
                                # print(outcome, file=log)
                                if outcome:
                                    print('DBUG: Success')
                                    print('DBUG: Success', file=log)
                            except Exception as er:
                                print(f'ERROR: cannot update {user}: {er}')
                                print(f'ERROR: cannot update {user}: {er}', file=log)
            except Exception as er:
                print(f'ERROR in line {line} : {er}')
                print(f'ERROR in line {line} : {er}', file=log)

        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'Execution ended at {endTime}')
        print(f'Execution ended at {endTime}', file=log)
