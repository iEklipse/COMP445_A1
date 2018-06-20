# COMP 445 - ASSIGNMENT 1
# Tri-Luong Steven Dien
# 27415281

import socket
import sys
import re


def send_request(command, host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        host = host.rstrip('\r\n')
        port = port.rstrip('\r\n')

        conn.connect((host, int(port)))

        if "httpc get" in command:
            request = get_request(command, host)
        if "httpc post" in command:
            request = post_request(command, host)

        encoded_request = request.encode("utf-8")
        conn.sendall(encoded_request)

        # MSG_WAITALL waits for full request or error
        encoded_response = conn.recv(4096, socket.MSG_WAITALL)

        decoded_response = encoded_response.decode("utf-8")
        response_body = encoded_response.decode("utf-8").split("\r\n\r\n")[1]

        if "302 FOUND" in decoded_response:
            redirect_check(decoded_response, command, host, port)
            return

        if "-v" in command:
            sys.stdout.write("\nReplied:" + decoded_response)
        else:
            sys.stdout.write("\nReplied:" + response_body)

        if "-o" in command:
            command.split("-o ")[1]
            filename = command.split("-o ")[1].rstrip("\r\n")
            output_file = open(filename, 'x')
            output_file.write(response_body)

    finally:
        conn.close()


def get_request(request, host):
    url = re.search("(?P<url>https?://[^\s]+)", request).group("url")

    if "-d" in request and "-f" in request:
        print("Cannot use [-d] or [-f] in a get request, program terminated")
        sys.exit()

    if "-h" in request:
        headers = "\r\n" + request[request.index("-h ") + 3:request.index(url)]
        request = "GET " + url \
            + " HTTP/1.0\r\n" \
            + "Host: " + host \
            + headers + "\r\n" \
            + "\r\n\r\n"
    else:
        request = "GET " + url \
            + " HTTP/1.0\r\n" \
            + "Host: " + host.rstrip('\r\n') \
            + "\r\n\r\n"

    return request


def post_request(request, host):
    url = re.search("(?P<url>https?://[^\s]+)", request).group("url")

    if "-d" in request and "-f" in request:
        print("Cannot use both [-d] and [-f] in the same request, program terminated")
        sys.exit()

    if "-d" in request or "-f" in request:
        if "-f" in request:
            filename = data = request[request.index("-f ") + 3:request.index(url) - 1]
            file = open(filename, 'r')
            data = file.read()
            temp = data.replace("\n", ", ")
            data = temp
        else:
            data = request[request.index("-d ") + 3:request.index(url) - 1]

        data_length = str(len(data))

        if "-h" in request:
            if "-f" in request:
                headers = request[request.index("-h ") + 3:request.index("-f")]
            else:
                headers = request[request.index("-h ") + 3:request.index("-d")]
            if " " in headers:
                modified_headers = headers.replace(' ', '\r\n')
                headers = modified_headers
        else:
            headers = ""

        if "Content-Length" not in request:
            request = "POST " + url \
                + " HTTP/1.0\r\n" \
                + "Host: " + host + "\r\n" \
                + headers \
                + "Content-Length: " + data_length \
                + "\r\n\r\n" \
                + data
        else:
            request = "POST " + url \
                + " HTTP/1.0\r\n" \
                + "Host: " + host + "\r\n" \
                + headers  \
                + "\r\n" \
                + data

    elif "-h" in request:
        headers = request[request.index("-h ") + 3:request.index(url)]
        if " " in headers:
            modified_headers = headers.replace(' ', '\r\n')
            headers = modified_headers

        request = "POST " + url \
            + " HTTP/1.0\r\n" \
            + "Host: " + host + "\r\n" \
            + headers \
            + "\r\n"

    else:
        request = "POST " + url \
                  + " HTTP/1.0\r\n" \
                  + "Host: " + host.rstrip('\r\n') \
                  + "\r\n\r\n"

    return request


def redirect_check(response, command, host, port):
    url = re.search("(?P<url>https?://[^\s]+)", command).group("url")
    url_without_path = "/".join(url.split("/", 3)[:3])
    new_location = response[response.index("Location: ") + 10:response.index("\r\nAccess-Control-Allow-Origin")]
    new_command = command.split(url)[0] + url_without_path + new_location

    send_request(new_command, host, port)

def help_command():
    print("\nhttpc is a curl-like application but supports HTTP protocol only.")
    print("usage: httpc command [arguments]")
    print("\nThe commands are:")
    print("\tget\texecutes a HTTP GET request and prints the response.")
    print("\tpost\texecutes a HTTP POST request and prints the response.")
    print("\thelp\tprints this screen.")
    print("\nUse \"httpc help [command]\" for more information about a command.")


def help_get_command():
    print("\nGet executes a HTTP GET request for a given URL.")
    print("usage: httpc get [-v] [-h key:value] URL")
    print("\n-v\tPrints the detail of the response such as protocol, status, and headers.")
    print("-h\tkey:value Associates headers to HTTP Request with the format 'key:value'.")


def help_post_command():
    print("\nPost executes a HTTP POST request for a given URL with inline data or from file.")
    print("usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL")
    print("\n-v\tPrints the detail of the response such as protocol, status, and headers.")
    print("-h\tkey:value Associates headers to HTTP Request with the format 'key:value'.")
    print("-d\tstring Associates an inline data to the body HTTP POST request.")
    print("-f\tfile Associates the content of a file to the body HTTP POST request.")
    print("\nEither [-d] or [-f] can be used but not both.")


print("Command/Request: ")
command = sys.stdin.readline(1024)
while "httpc help" in command:
    if "httpc help get" in command:
        help_get_command()
    elif "httpc help post" in command:
        help_post_command()
    elif "httpc help" in command:
        help_command()

    print("\nCommand/Request: ")
    command = sys.stdin.readline(1024)

if "httpc get" in command or "httpc post" in command:
    print("Host: ")
    host = sys.stdin.readline(1024)
    print("Port: ")
    port = sys.stdin.readline(1024)
    send_request(command, host, port)
else:
    print("Wrong command/request, program terminated.")
