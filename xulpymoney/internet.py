## THIS IS FILE IS FROM https://github.com/turulomio/reusingcode IF YOU NEED TO UPDATE IT PLEASE MAKE A PULL REQUEST IN THAT PROJECT
## DO NOT UPDATE IT IN YOUR CODE IT WILL BE REPLACED USING FUNCTION IN README

from socket import create_connection

## Checks if there is internet
def is_there_internet():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False