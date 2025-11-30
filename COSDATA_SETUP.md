🦁 Cosdata Database Setup Guide

Kosdra relies on Cosdata, a high-performance hybrid vector database. Follow these steps to get the database server up and running on your local machine.

1. Install Cosdata

Linux / macOS

Open your terminal and run the official installation script:

curl -sL [https://cosdata.io/install.sh](https://cosdata.io/install.sh) | bash


This will download the cosdata binary to your current directory.

Windows

You will need to use Docker or WSL2 (Windows Subsystem for Linux).

Docker: docker pull cosdataio/cosdata:latest

WSL2: Follow the Linux instructions above inside your WSL terminal.

2. Start the Server

You need to start the server in a separate terminal window and keep it running while you use the app.

Linux / macOS (Native Binary)

Run this command from the folder where you installed Cosdata:

./cosdata --host 0.0.0.0 --port 8443 --admin-key Admin1h


--host 0.0.0.0: Ensures the server listens on all network interfaces (fixes connection issues).

--port 8443: The standard port for Cosdata.

--admin-key Admin1h: Sets the admin password to "Admin1h" (matches the app's config).

Docker

If you prefer Docker:

docker run -d -p 8443:8443 -p 50051:50051 \
  -e COSDATA_ADMIN_KEY=Admin1h \
  cosdataio/cosdata:latest


3. Verification

To make sure the server is running correctly, open a new terminal and ping the health endpoint:

curl [http://127.0.0.1:8443/health](http://127.0.0.1:8443/health)


You should receive a response like: {"status":"ok"}.

4. Troubleshooting

"Connection Refused" or "Database Full" Errors
If you encounter errors after restarting the app multiple times, you may need to perform a "Hard Reset" of the database data.

Stop the Server: Press Ctrl+C in the server terminal.

Delete Data: Remove the data directory created by Cosdata.

rm -rf data cosdata_data


Restart: Run the start command from Step 2 again.

Re-Seed: Run the seed script to repopulate the database.

PYTHONPATH=. python -m kosdra.scripts.seed_db
