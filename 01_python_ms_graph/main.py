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
    # TODO
    return

async def display_access_token(graph: Graph):
    # TODO
    return

async def list_inbox(graph: Graph):
    """
    Asynchronously fetches and prints the list of messages in the user's inbox using the Microsoft Graph API.

    Parameters:
    - graph: An instance of the Graph class, which should be authenticated and capable of making API calls.

    Returns:
    - A list of message dictionaries if the request is successful, otherwise None.
    """
    try:
        # Make an API call to list messages in the user's inbox
        response = await graph.get('me/messages')

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the response to extract the messages
            messages = response.json().get('value', [])

            # Process and print the messages
            for message in messages:
                # Extract and print the subject and sender's email address
                subject = message.get('subject', 'No subject')
                sender_email = message.get('from', {}).get('emailAddress', {}).get('address', 'No sender')
                print(f"Subject: {subject}, From: {sender_email}")

            return messages
        else:
            print(f"Failed to list messages. Status code: {response.status_code}")
            return None
    except Exception as e:
        # Catch any exceptions that occur during the API call or processing
        print(f"An error occurred: {e}")
        return None

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
