---

## ⚙️ Setup Instructions

### 1. Clone Repo
```bash
git clone <your_repo_url>
cd multi_tool_med_agent
2. Create Virtual Environment
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\activate        # Windows
3. Install Dependencies
pip install -r requirements.txt
4. Environment Variables
Copy the example file and add your keys:
cp .env.example .env
GitHub Models (for AI SQL generation):
GITHUB_TOKEN=ghp_...         # GitHub PAT with models:read scope
GITHUB_BASE_URL=https://models.inference.ai.azure.com
GITHUB_MODEL=gpt-4o-mini
Tavily API (for web search):
TAVILY_API_KEY=tvly_...
5. Data Preparation
For convenience in this assignment, the data/ (CSV) and db/ (SQLite) folders are already included.
If you want to rebuild from scratch:

# Download from Kaggle
python scripts/download_kaggle.py

# Convert CSV → SQLite
python scripts/build_sqlite.py
🚀 Run the Agent
python main.py
You’ll see:
Multi-Tool Medical Agent
Type 'exit' to quit.
>>
🧪 Example Queries
Database Queries
Show rows where outcome=1
How many rows where diagnosis='M'
List 10 records where glucose > 150
How many patients are older than 60 with cholesterol > 250?
Web Queries
What are the common symptoms of heart disease?
What is a malignant tumor?
How can type 2 diabetes be prevented?
What treatments are available for breast cancer?