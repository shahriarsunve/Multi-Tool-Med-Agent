import os
from dotenv import load_dotenv
from agent.router import MultiToolMedicalAgent

def main():
    load_dotenv()
    agent = MultiToolMedicalAgent()

    print("Multi-Tool Medical Agent 🧠 (GitHub Models Edition)")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            q = input(">> ")
        except EOFError:
            break
        if q.strip().lower() in {"exit", "quit"}:
            break
        resp = agent.ask(q)
        route = resp.get("route")
        tool = resp.get("tool")
        sql = resp.get("sql")
        error = resp.get("error")
        result = resp.get("result")

        if route == "db" and sql:
            print(f"\n[DB Route via {tool}]")
            print(f"SQL: {sql}")
        elif route == "web":
            print(f"\n[Web Route via {tool}]")
        if error:
            print(f"Error: {error}")
        print(result, "\n")

if __name__ == "__main__":
    main()
