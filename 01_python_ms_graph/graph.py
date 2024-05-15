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

        self.device_code_credential = DeviceCodeCredential(
            client_id, tenant_id=tenant_id)
        self.user_client = GraphServiceClient(self.device_code_credential,
                                              graph_scopes)

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
        self.save_login_info()


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

    async def send_mail(self, subject: str, body: str, recipient: str):
        """
        This method sends an email using the Microsoft Graph API.
        It takes three parameters: subject, body, and recipient.
        The subject and body are strings representing the email's subject and body content.
        The recipient is a string representing the email address of the recipient.
        """

        # Create a new Message object to represent the email.
        message = Message()
        # Set the subject of the email.
        message.subject = subject

        # Create an ItemBody object for the email body and set its content type to Text.
        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        # Set the content of the email body.
        message.body.content = body

        # Create a Recipient object for the email recipient.
        to_recipient = Recipient()
        # Create an EmailAddress object and set its address to the recipient's email address.
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = recipient
        # Initialize the to_recipients list and append the recipient to it.
        message.to_recipients = []
        message.to_recipients.append(to_recipient)

        # Create a SendMailPostRequestBody object and set its message to the created email.
        request_body = SendMailPostRequestBody()
        request_body.message = message

        # Send the email using the Microsoft Graph API.
        await self.user_client.me.send_mail.post(body=request_body)




    # extra functions not in tutorial

    def load_login_info(self):
        token_file_path = self.settings.get('tokenFilePath', 'pri/tokens.json')
        if os.path.exists(token_file_path):
            try:
                with open(token_file_path, 'r') as f:
                    tokens = json.load(f)
                    self.device_code_credential.token = tokens.get('access_token')
                    self.logger.info(f"Loaded access token: {self.device_code_credential.token}")
            except Exception as e:
                self.logger.error(f"Failed to load login info: {e}")
        else:
            self.logger.warning(f"Token file not found: {token_file_path}")


    def save_login_info(self):
        token_file = 'pri/tokens.json'
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)

        # Validate the token_file path
        if not os.path.isabs(token_file):
            token_file = os.path.join(os.getcwd(), token_file)

        tokens = {
            'graph_scopes': graph_scopes,
            'access_token': access_token.token,
            # Uncommenting refresh_token if needed
            #'refresh_token': access_token.refresh_token
        }

        try:
            with open(token_file, 'w') as f:
                json.dump(tokens, f)
            print(f"Login info saved successfully to {token_file}")
        except IOError as e:
            print(f"An error occurred while saving login info: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
