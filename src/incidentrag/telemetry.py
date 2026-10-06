from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class Telemetry:
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    requests: int = 0
    searches: int = 0
    answers: int = 0
    abstentions: int = 0
    failures: int = 0
    total_latency_ms: float = 0.0

    @contextmanager
    def measure(self, operation: str) -> Iterator[None]:
        start = time.perf_counter()
        with self._lock:
            self.requests += 1
            if operation == "search":
                self.searches += 1
            elif operation == "answer":
                self.answers += 1
        try:
            yield
        except Exception:
            with self._lock:
                self.failures += 1
            raise
        finally:
            latency = (time.perf_counter() - start) * 1000.0
            with self._lock:
                self.total_latency_ms += latency

    def record_abstention(self) -> None:
        with self._lock:
            self.abstentions += 1

    def snapshot(self) -> dict[str, float | int]:
        with self._lock:
            average = self.total_latency_ms / self.requests if self.requests else 0.0
            return {
                "requests": self.requests,
                "searches": self.searches,
                "answers": self.answers,
                "abstentions": self.abstentions,
                "failures": self.failures,
                "avg_latency_ms": round(average, 3),
            }


def configure_json_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            return json.dumps(
                {
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                },
                sort_keys=True,
            )

    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
