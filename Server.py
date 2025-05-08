import socket
import psycopg2
from datetime import datetime, timedelta

# Database connection string for NeonDB
NEONDB_CONNECTION = "postgresql://neondb_owner:npg_NFZwczXd35LO@ep-still-snowflake-a5wer42j-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Binary Tree implementation for storing and comparing device electricity consumption
class TreeNode:
    def __init__(self, key, value):
        self.key = key  # Stores kWh value
        self.value = value  # Stores device name
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    # Inserts a new node into the binary tree
    def insert(self, key, value):
        def _insert(node, key, value):
            if not node:
                return TreeNode(key, value)
            if key < node.key:
                node.left = _insert(node.left, key, value)
            else:
                node.right = _insert(node.right, key, value)
            return node
        self.root = _insert(self.root, key, value)

    # Finds a value in the tree based on key
    def find(self, key):
        def _find(node, key):
            if not node:
                return None
            if key == node.key:
                return node.value
            elif key < node.key:
                return _find(node.left, key)
            else:
                return _find(node.right, key)
        return _find(self.root, key)

# Main query handler that processes all 3 options for user
def handle_query(query, cursor):
    try:
        print(f"→ Handling query: {query}")

        # Query for average moisture levels from moisture sensor
        if "average moisture" in query:
            print("→ Running simulated moisture query...")
            cursor.execute('''
                SELECT AVG(CAST(payload->>'Moisture Meter - moisture meter sensor' AS FLOAT))
                FROM lab8_virtual
                WHERE topic = 'Smart'
                AND (time AT TIME ZONE 'UTC' AT TIME ZONE 'PST') >= (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'PST') - INTERVAL '3 HOURS';
            ''')
            result = cursor.fetchone()[0]
            print("→ Moisture result:", result)
            return f"Simulated average moisture (from Moisture Meter - moisture meter sensor): {result:.2f} % RH" if result else "No data found."

        # Query for average water consumption from water sensor
        elif "average water consumption" in query:
            print("→ Running simulated water query...")
            cursor.execute('''
                SELECT 
                    SUM(CAST(payload->>'YF-S201 - water sensor' AS FLOAT)) / NULLIF(COUNT(*), 0)
                FROM lab8_virtual
                WHERE topic = 'Smart'
            ''')
            result = cursor.fetchone()[0]
            print("→ Water result:", result)
            return f"Simulated average water consumption: {result:.2f} gallons" if result else "No data found."

        # Query to determine which device consumed the most electricity
        elif "consumed more electricity" in query:
            print("→ Running separate electricity queries for each device...")

            voltage = 120  # Standard voltage in volts
            tree = BinaryTree() 

            # Query for Fridge electricity consumption
            cursor.execute("""
                SELECT 
                    SUM((payload->>'ACS712 - ammeter')::FLOAT),
                    MIN(time), MAX(time)
                FROM lab8_virtual
                WHERE payload->>'parent_asset_uid' = '91t-37n-pvq-vvq'
            """)
            fridge_result = cursor.fetchone()
            amps_fridge, start_f, end_f = fridge_result
            if amps_fridge and start_f and end_f:
                # Calculate kWh: (amps * voltage * hours) / 1000
                fridge_kwh = (amps_fridge * voltage * (end_f - start_f).total_seconds() / 3600) / 1000
                tree.insert(fridge_kwh, "Fridge")

            # Query for Fridge 2 electricity consumption
            cursor.execute("""
                SELECT 
                    SUM((payload->>'sensor 2 47989f9f-1e91-4d82-bdc3-d8a652be5b54')::FLOAT),
                    MIN(time), MAX(time)
                FROM lab8_virtual
                WHERE payload->>'parent_asset_uid' = '47989f9f-1e91-4d82-bdc3-d8a652be5b54'
            """)
            fridge2_result = cursor.fetchone()
            amps_fridge2, start_f2, end_f2 = fridge2_result
            if amps_fridge2 and start_f2 and end_f2:
                fridge2_kwh = (amps_fridge2 * voltage * (end_f2 - start_f2).total_seconds() / 3600) / 1000
                tree.insert(fridge2_kwh, "Fridge 2")

            # Query for Dishwasher electricity consumption
            cursor.execute("""
                SELECT 
                    SUM((payload->>'ACS712 - dishwasherammeter')::FLOAT),
                    MIN(time), MAX(time)
                FROM lab8_virtual
                WHERE payload->>'parent_asset_uid' = '773-bvr-hey-8c3'
            """)
            dishwasher_result = cursor.fetchone()
            amps_dishwasher, start_d, end_d = dishwasher_result
            if amps_dishwasher and start_d and end_d:
                dishwasher_kwh = (amps_dishwasher * voltage * (end_d - start_d).total_seconds() / 3600) / 1000
                tree.insert(dishwasher_kwh, "Dishwasher")

            # Find the device with maximum electricity consumption using binary tree
            def find_max(node):
                if not node.right:
                    return node.key, node.value
                return find_max(node.right)

            if tree.root:
                max_kwh, max_device = find_max(tree.root)
                return f"{max_device} consumed the most electricity with {max_kwh:.2f} kWh"
            else:
                return "No electricity data found."
    

    except Exception as e:
        print("SERVER ERROR:", e)
        return "Server error: something went wrong while processing your request."

# Main server function that sets up the socket connection and handles client requests
def main():
    host = input("Enter server IP address (e.g., 127.0.0.1): ")
    port = int(input("Enter port to listen on (e.g., 5050): "))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")

            # Connect to the database
            db_conn = psycopg2.connect(NEONDB_CONNECTION)
            cursor = db_conn.cursor()

            # Main server loop - continuously process client queries
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                query = data.decode()
                print(f"Received query: {query}")

                response = handle_query(query, cursor)
                conn.sendall(response.encode())

            cursor.close()
            db_conn.close()

if __name__ == "__main__":
    main()
