# 🦁 Cosdata Database Setup Guide

Kosdra relies on **Cosdata**, a high-performance **hybrid vector database**.  
Follow these steps to install and run the Cosdata server locally.

---

## 1. 🔧 Install Cosdata

### **Linux / macOS**

Run the official installation script:

```bash
curl -sL https://cosdata.io/install.sh | bash
````

This will download the `cosdata` binary to your current directory.

---

### **Windows**

You must use **Docker** or **WSL2**.

#### **Option A — Docker**

```bash
docker pull cosdataio/cosdata:latest
```

#### **Option B — WSL2**

Open your WSL terminal and follow the **Linux/macOS** installation instructions.

---

## 2. 🚀 Start the Server

Open a **new terminal window** and run the server.
Keep this terminal open while using the app.

---

### **Linux / macOS (Native Binary)**

Navigate to the directory where Cosdata was installed:

```bash
start-cosdata
```

**Enter/Set Admin Key**

* `Admin Key:` 

---

## 3. 🩺 Verify the Server

Run the health check:

```bash
curl http://127.0.0.1:8443/health
```

Expected output:

```json
{"status":"ok"}
```

This confirms the server is up and running.

---

## 4. 🛠️ Troubleshooting

### **❌ “Connection Refused” or “Database Full” Errors**

This happens if you restart the app repeatedly or the database becomes corrupted.

Follow these steps:

#### 1️⃣ Stop the server

Press **Ctrl + C** in the server terminal.

#### 2️⃣ Delete existing Cosdata data

Remove the data directories:

```bash
rm -rf data cosdata_data
```

#### 3️⃣ Restart the server
