## 🦁 Kosdra: The AI-Native Recruitment Engine

Stop guessing. Start hiring with precision.

Kosdra is an intelligent recruitment platform that solves the **"Semantic Gap"** in hiring by combining the power of **Vector Search** (for skills & context) with **Keyword Search** (for strict requirements). Built on **Cosdata.io**, it ensures recruiters find the best talent — not just candidates who stuffed their resumes with SEO keywords.

---

## 🛑 The Problem: Why Hiring is Broken

Recruitment tools today fall into two traps:

### **1. Keyword Search Failures**
If a candidate writes *"mentored juniors"* but the recruiter searches for *"Leadership"*, a standard keyword search misses them entirely.  
👉 You lose great talent because of vocabulary mismatches.

### **2. Vector Search Failures**
Pure AI search is too **fuzzy**.  
If a job requires a *"Top Secret Clearance"* or *"US Citizenship"*, a pure vector search may still return a brilliant foreign national candidate because their skills match.  
👉 This wastes the recruiter’s time.

---

## ✅ The Solution: Hybrid Search

Kosdra uses a **Hybrid Search Engine** powered by Cosdata to get the best of both worlds:

- **Vectors (Dense Index):**  
  Understand that *"Kubernetes"* implies *"Cloud Skills"* and *"Mentoring"* implies *"Leadership"*.

- **Keywords (Sparse Index):**  
  Strictly enforce mandatory requirements like *Visa Status*, *Security Clearance*, or *Certifications*.

---

## 🚀 Key Features

### 🔍 Context-Aware Search
Find candidates who **mean** what you're looking for, even if they use different words.

### 🛡️ Precision Filters (The “Trap” Solvers)
- **Citizenship/Visa Filter:** Instantly filter out candidates who don't meet legal work requirements.  
- **Clearance Levels:** Enforce *Top Secret* or *Secret* clearance with 100% accuracy.

### 📊 Recruitment Analytics
A built-in dashboard to visualize the talent pool by:
- Skill  
- Experience  
- Location  

### 📁 Seamless Workflow
- **Upload:** Drag & Drop PDF/Word resumes  
- **Parse:** Automatically extract text and metadata  
- **Shortlist:** One-click shortlisting + CSV export  

---

## 🛠️ Tech Stack

- **Database:** Cosdata.io (Hybrid Vector Database)  
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`  
- **Frontend:** Streamlit  
- **Backend:** Python (Modular Architecture)  
- **Parsing:** PyPDF  

---

## 🏃‍♂️ Quick Start

### **1. Clone the Repository**
```bash
git clone https://github.com/harshal-rembhotkar/kosdra.git
cd kosdra
````

### **2. Start Cosdata Server**

Follow the instructions in `COSDATA_SETUP.md` to get the database running.

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Seed the Database**

(Loads mock “Trap” candidates for testing)

```bash
PYTHONPATH=. python -m kosdra.scripts.seed_db
```

### **5. Run the App**

```bash
PYTHONPATH=. streamlit run kosdra/main.py
```

---

## 🏆 Hackathon Goals

This project was built for the **Cosdata Hackathon 2025** to demonstrate the power of Hybrid Search in a real-world, high-stakes application.

By leveraging Cosdata’s **transactional integrity** and **dual-indexing capabilities**, Kosdra proves that AI can be both **smart** and **precise**.

Demo link: [Click here](https://youtu.be/EP92xVBYG0M)
