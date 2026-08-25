from __future__ import annotations

import argparse
import json

from tokenaudit_knowledge.cli import run_rag_test


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the small Fable 5 RAG test set")
    parser.add_argument("--env-file", action="append", required=True)
    args = parser.parse_args()
    result = run_rag_test(args)
    print(json.dumps(result["metrics"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
