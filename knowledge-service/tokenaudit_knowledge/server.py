from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Any

from .hybrid_retriever import HybridAuditRetriever, compact_evidence


class KnowledgeApplication:
    def __init__(self, retriever: HybridAuditRetriever) -> None:
        self.retriever = retriever
        self.retrieval_lock = threading.Lock()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "spec_collection": self.retriever.spec_store.collection,
            "behavior_collection": self.retriever.behavior_store.collection,
            "behavior_stats": self.retriever.behavior_store.stats(),
        }

    def retrieve(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_id = str(payload.get("model_id") or "").strip()
        query = str(payload.get("query") or "").strip()
        if not model_id or not query:
            raise ValueError("model_id and query are required")
        # Milvus Lite has a single owner process. Retrieval is short and serialized;
        # audit-model and target-model work remains concurrent outside this service.
        with self.retrieval_lock:
            return compact_evidence(self.retriever.retrieve(model_id=model_id, query=query))


def make_handler(application: KnowledgeApplication) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "TokenAuditKnowledge/1.0"

        def do_GET(self) -> None:  # noqa: N802
            if self.path.rstrip("/") != "/health":
                self._write(404, {"error": "not_found"})
                return
            self._write(200, application.health())

        def do_POST(self) -> None:  # noqa: N802
            if self.path.rstrip("/") != "/retrieve":
                self._write(404, {"error": "not_found"})
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
                if length <= 0 or length > 2_000_000:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("JSON object required")
                self._write(200, application.retrieve(payload))
            except ValueError as exc:
                self._write(400, {"error": str(exc)})
            except Exception as exc:
                self._write(500, {"error": type(exc).__name__, "message": str(exc)[:500]})

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _write(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="TokenAudit local knowledge retrieval service")
    parser.add_argument("--env-file", action="append", default=[])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8091)
    args = parser.parse_args()
    retriever = HybridAuditRetriever.load(args.env_file)
    application = KnowledgeApplication(retriever)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(application))
    try:
        print(json.dumps({"status": "ready", "host": args.host, "port": args.port, **application.health()}, ensure_ascii=False), flush=True)
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
        retriever.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
