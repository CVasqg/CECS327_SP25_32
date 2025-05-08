# CECS327_SP25_32
Assignment 8 focuses on using 2 VMs that communicate with each other using a Client and Server file. Both files connect to a database in NeonDB, where they can access data from Dataniz. In dataniz, 3 Smart devices are set up and generating data.

* Before getting started, make sure to download psycopg2. This allows us to seamlessly use python with postgresql.
  In your command line type:

    **pip install psycopg2**

* Server must run before Client or else this will not work.

* Once psycopg2 is installed, go to your terminal on your first VM and type this in to run the Server.py file.

 ** python Server.py**

* Then do the same for Client.py on your second VM

 ** python Client.py**

* Both files should be runnning and user should be able to view data on their devices.

