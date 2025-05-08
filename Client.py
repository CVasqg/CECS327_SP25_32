# Client.py


import socket

def main():
    server_ip = input("Enter server IP address: ")  # Get IP from user
    server_port = int(input("Enter server port number: "))  # Get port from user

    valid_queries = {
        "1": "What is the average moisture inside my kitchen fridge in the past three hours?",
        "2": "What is the average water consumption per cycle in my smart dishwasher?",
        "3": "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        
        while True:
            print("\nSelect a query:")
            for key, query in valid_queries.items():
                print(f"{key}. {query}")
            print("Q. Quit")

            choice = input("Enter your choice: ").strip()

            if choice.upper() == 'Q':
                print("Exiting client.")
                break

            if choice not in valid_queries:
                print("Sorry, this query cannot be processed. Please try one of the listed options.")
                continue

            query_to_send = valid_queries[choice]
            s.sendall(query_to_send.encode())
            data = s.recv(4096)

            print("\nResult from server:")
            print(data.decode())

if __name__ == "__main__":
    main()