from __future__ import annotations

import argparse

from tokenaudit_knowledge.cli import test_mixed_rag


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the TokenAudit mixed-model Top-K and Voyage rerank demo"
    )
    parser.add_argument("--env-file", action="append", required=True)
    args = parser.parse_args()
    return test_mixed_rag(args)


if __name__ == "__main__":
    raise SystemExit(main())
