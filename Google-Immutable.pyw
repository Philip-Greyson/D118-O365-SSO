from __future__ import print_function

import os.path

import json
from typing import get_type_hints

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os # needed for environement variable reading
from datetime import *


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.group', 'https://www.googleapis.com/auth/admin.directory.group.member', 'https://www.googleapis.com/auth/apps.licensing']


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
    with open('Immutable-Ids.csv', 'r') as source:
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'Execution started at {startTime}')
        print(f'Execution started at {startTime}', file=log)

        # get all users in our domain and their immutable ID if they have one, stored into a dictionary for easier querying than one at a time api calls
        userDict = {} # define dict that will contain sub-dict for each user containing their email and immutable id
        userToken = '' # initialize blank userToken for use in looping query
        while userToken is not None: # do a while loop while we still have a next page of results
            userResults = service.users().list(customer='my_customer', orderBy='email', projection='full', pageToken=userToken).execute() # return all users in our domain
            userToken = userResults.get('nextPageToken')
            users = userResults.get('users', [])
            for user in users:
                try:
                    # print(user)
                    # print(user, file=log)
                    email = user.get('primaryEmail', []) # get their email
                    currentImmutableID = user.get('customSchemas', {}).get('Office_365', {}).get('immutableID2') # get the value currently in their immutable id field, return a blank dict at each time so that we dont error out if they have no values
                    if email is not None and currentImmutableID is not None:
                        # print(f'INFO: Email: {email} - Current ID: {currentImmutableID}')
                        # print(f'INFO: Email: {email} - Current ID: {currentImmutableID}', file=log)
                        userDict.update({email : currentImmutableID}) # add the email : id entry to the dict
                except Exception as er:
                    print(f'ERROR on user {user}')
                    print(f'ERROR on user {user}', file=log)

        # print(userDict)

        # go through each line in the input IDs file, check against their current id in their profile, and update the profile if neccessary
        lines = source.readlines() # read all the lines of the immutable ids file and store them in a list
        for line in lines:
            try:
                if line[1] != '#': # ignore lines that start with a pound sign
                    line = line.strip() # strip out new line characters, whitespace, etc
                    split = line.split(',')
                    user = split[0].strip('"').lower() # strip out the double quotes, and convert to lowercase for better readability
                    immutableID = split[1].strip('"') # strip out double quotes
                    # print(f'User: {user} - ID: {immutableID}')

                    currentImmutableID = userDict.get(user)
                    # print(f'INFO: User: {user} - ID: {immutableID} - Current: {currentImmutableID}')
                    if immutableID != currentImmutableID:
                        print(f'ACTION: User {user} needs ID updated from {currentImmutableID} to {immutableID}')
                        print(f'ACTION: User {user} needs ID updated from {currentImmutableID} to {immutableID}', file=log)
                        bodyDict = {'customSchemas' : {'Office_365' : {'immutableID2' : immutableID}}}
                        try:
                            outcome = service.users().update(userKey = user, body=bodyDict).execute() # does the actual updating of the user profile
                            if outcome:
                                print(f'\tINFO: Success')
                                print(f'\tINFO: Success', file=log)
                        except Exception as er:
                            if 'Resource Not Found: userKey' in str(er):
                                print(f'\tWARNING: cannot update {user} as they were not found in our domain')
                                print(f'\tWARNING: cannot update {user} as they were not found in our domain', file=log)
                            elif 'Not Authorized to access this resource/api' in str(er):
                                print(f'\tWARNING: cannot update {user} as the email is not in our domain')
                                print(f'\tWARNING: cannot update {user} as the email is not in our domain', file=log)
                            else:
                                print(f'ERROR: cannot update {user}: {er}')
                                print(f'ERROR: cannot update {user}: {er}', file=log)
            except Exception as er:
                print(f'ERROR in line {line} : {er}')
                print(f'ERROR in line {line} : {er}', file=log)
        
        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'Execution ended at {endTime}')
        print(f'Execution ended at {endTime}', file=log)