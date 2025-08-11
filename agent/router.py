import os
from typing import Dict, Any, Optional
from tools.db_tool import HeartDiseaseDBTool, CancerDBTool, DiabetesDBTool
from tools.web_tool import MedicalWebSearchTool

USE_LLM = bool(os.getenv("GITHUB_TOKEN"))

def _rule_based_route(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["what is", "define", "symptom", "treatment", "treat", "cure", "causes", "risk factor", "prevention"]):
        return "web"
    if any(w in q for w in ["how many", "average", "count", "mean", "median", "min", "max", "distribution", "show rows", "where "]):
        return "db"
    if any(w in q for w in ["heart", "cancer", "diabetes"]):
        return "db"
    return "web"

def _pick_db_tool(question: str, heart, cancer, diabetes):
    q = question.lower()
    if any(k in q for k in ["heart", "chol", "cp", "thal", "thalach", "target"]):
        return heart
    if any(k in q for k in ["tumor", "cancer", "malignant", "benign", "diagnosis"]):
        return cancer
    if any(k in q for k in ["diab", "glucose", "insulin", "pregnancies", "bmi", "outcome"]):
        return diabetes
    return heart

def _maybe_llm_sql(question: str, table_hint: str) -> Optional[str]:
    if not USE_LLM:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("GITHUB_TOKEN"), base_url=os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com"))
        model = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
        prompt = f"""You are an expert data engineer. Write a single SQLite SELECT statement for the following user question.
- Only use the table `{table_hint}`.
- Return at most 25 rows.
- Output SQL only (no explanations, no backticks).

Question: {question}
"""
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        sql = resp.choices[0].message.content.strip()
        if not sql.lower().startswith("select"):
            return None
        if table_hint not in sql:
            return None
        return sql
    except Exception:
        return None

class MultiToolMedicalAgent:
    def __init__(self, db_dir: str = "db"):
        self.heart = HeartDiseaseDBTool(os.path.join(db_dir, "heart_disease.db"))
        self.cancer = CancerDBTool(os.path.join(db_dir, "cancer.db"))
        self.diabetes = DiabetesDBTool(os.path.join(db_dir, "diabetes.db"))
        self.web = MedicalWebSearchTool(provider="tavily")

    def ask(self, question: str) -> Dict[str, Any]:
        route = _rule_based_route(question)
        if route == "web":
            return {"route":"web", **self.web.run(question)}

        tool = _pick_db_tool(question, self.heart, self.cancer, self.diabetes)
        table_hint = tool.table_hint
        sql = _maybe_llm_sql(question, table_hint=table_hint)
        return {"route":"db", **tool.run(question, sql=sql)}
