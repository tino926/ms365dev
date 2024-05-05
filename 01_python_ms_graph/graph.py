from configparser import SectionProxy
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder)
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody)
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress

import json
import os

class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)

    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token

    async def get_user(self):
        # Only request specific properties using $select
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        # ^ this cause: type object 'UserItemRequestBuilder' has no attribute 'UserItemRequestBuilderGetRequestConfiguration'
        #   need rolling back to msgraph-sdk==1.2.0

        user = await self.user_client.me.get(request_configuration=request_config)

        return user

    async def get_inbox(self):
        """
        Retrieves the latest 25 messages from the user's inbox, including 
        specific properties such as sender, read status, 
        received date and time, and subject. The messages are sorted by received 
        date and time in descending order.

        Returns:
            A list of Message objects containing the requested properties of the 
            latest messages in the inbox.
        """
        # Define the query parameters for the request
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['from', 'isRead', 'receivedDateTime', 'subject'],
            # Get at most 25 results
            top=25,
            # Sort by received time, newest first
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        # Make the request to get messages from the inbox
        messages = await self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
            request_configuration=request_config)
        return messages

    # extract functions not in tutorial

    def load_tokens(self):
        token_file = 'tokens.json'
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                tokens = json.load(f)
                self.device_code_credential.token = tokens.get('token')
                self.device_code_credential.refresh_token = tokens.get('refresh_token')

    def save_tokens(self):
        token_file = 'tokens.json'
        tokens = {
            'token': self.device_code_credential.token,
            'refresh_token': self.device_code_credential.refresh_token
        }
        with open(token_file, 'w') as f:
            json.dump(tokens, f)

    async def send_mail(self, subject: str, body: str, recipient: str):

        # Create a new Message object
        message = Message()
        
        # Set the subject and body of the message
        message.subject = subject
        message.body = ItemBody(contentType=BodyType.TEXT, content=body)
        
        # Create a new Recipient object for the recipient email address
        recipient_email = Recipient(emailAddress=EmailAddress(address=recipient))
        
        # Add the recipient to the message
        message.to_recipients = [recipient_email]

