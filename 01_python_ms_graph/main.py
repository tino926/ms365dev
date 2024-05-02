import asyncio
import configparser
import sys

print(f'Python version: {sys.version}\n') # Print the Python version

from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from graph import Graph

async def main():
    print('Python Graph Tutorial\n')

    # Load settings
    config = configparser.ConfigParser()
    config.read(['pri/config.cfg', 'pri/config.dev.cfg'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)

    await greet_user(graph)

    choice = -1

    while choice != 0:
        print('Please choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. List my inbox')
        print('3. Send mail')
        print('4. Make a Graph call')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        try:
            if choice == 0:
                print('Goodbye...')
            elif choice == 1:
                await display_access_token(graph)
            elif choice == 2:
                await list_inbox(graph)
            elif choice == 3:
                await send_mail(graph)
            elif choice == 4:
                await make_graph_call(graph)
            else:
                print('Invalid choice!\n')
        except ODataError as odata_error:
            print('Error:')
            if odata_error.error:
                print(odata_error.error.code, odata_error.error.message)

async def greet_user(graph: Graph):

    user = await graph.get_user()

    if user is None:
        print("log in first")
        return
    else:
        print('Hello,', user.display_name)
        # For Work/school accounts, email is in mail property
        # Personal accounts, email is in userPrincipalName
        print('Email:', user.mail or user.user_principal_name, '\n')

    return

async def display_access_token(graph: Graph):
    """
    Asynchronously retrieves and prints the user access token from the Microsoft Graph API.

    Parameters:
    - graph: An instance of the Graph class, which should be authenticated and capable of making API calls.

    Returns:
    - None. The function prints the user access token to the console.
    """
    token = await graph.get_user_token()
    print('User token:', token, '\n')


async def list_inbox(graph: Graph):
    # Get the inbox of the user
    message_page = await graph.get_inbox()
    # Check if the message page is not empty and has a value
    if message_page and message_page.value:
        # Output each message's details
        for message in message_page.value:
            # Print the subject of the message
            print('Message:', message.subject)
            # Check if the message has a from field and an email address
            if (
                message.from_ and
                message.from_.email_address
            ):
                # Print the name of the email address if it exists
                print('  From:', message.from_.email_address.name or 'NONE')
            else:
                # Print NONE if the message does not have a from field or email address
                print('  From: NONE')
            # Print the status of the message
            print('  Status:', 'Read' if message.is_read else 'Unread')
            # Print the date and time the message was received
            print('  Received:', message.received_date_time)

        # If @odata.nextLink is present
        more_available = message_page.odata_next_link is not None
        # Print if more messages are available
        print('\nMore messages available?', more_available, '\n')


async def send_mail(graph: Graph):
    # TODO
    return

async def make_graph_call(graph: Graph):
    # TODO
    return


# show current directory
print(f'Current directory: {sys.path[0]}\n')

# Run main
asyncio.run(main())
