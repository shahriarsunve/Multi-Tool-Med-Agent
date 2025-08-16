import sqlite3
from typing import Any, Dict, Optional
from tabulate import tabulate
from .base import Tool

class SQLiteQueryTool(Tool):
    def __init__(self, db_path: str, table_hint: Optional[str] = None, name: str = "SQLiteQueryTool"):
        self.db_path = db_path
        self.table_hint = table_hint
        self.name = name

    def describe(self) -> str:
        return f"{self.name}: Query {self.db_path} (table hint: {self.table_hint})"

    def _naturalize(self, rows, cols) -> str:
        if not rows:
            return "No rows matched your query."
        return tabulate(rows, headers=cols, tablefmt="github")

    def _sql_from_question(self, question: str) -> str:
        ql = question.lower()
        cond = "1=1"
        if " where " in ql:
            after = ql.split(" where ", 1)[1]
            frag = after.split()[0]
            if "=" in frag:
                col, val = frag.split("=", 1)
                col = col.strip().replace(" ", "_").lower()
                # strip existing quotes if user included them
                val = val.strip().strip("'\"")
                # if numeric, keep raw, else wrap in single quotes
                if val.replace(".", "", 1).isdigit():
                    cond = f"{col} = {val}"
                else:
                    cond = f"{col} = '{val}'"
        table = self.table_hint or "main_table"
        return f"SELECT * FROM {table} WHERE {cond} LIMIT 25;"


    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        sql = kwargs.get("sql") or self._sql_from_question(query)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
        return {
            "tool": self.name,
            "sql": sql,
            "result": self._naturalize(rows, cols),
        }

class HeartDiseaseDBTool(SQLiteQueryTool):
    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_hint="heart_metrics", name="HeartDiseaseDBTool")

class CancerDBTool(SQLiteQueryTool):
    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_hint="cancer_features", name="CancerDBTool")

class DiabetesDBTool(SQLiteQueryTool):
    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_hint="diabetes_metrics", name="DiabetesDBTool")
