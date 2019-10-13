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