from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class LedgerEvent:
    run_id: str
    step: int
    event_type: str
    timestamp_utc: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "step": self.step,
            "event_type": self.event_type,
            "timestamp_utc": self.timestamp_utc,
            "payload": self.payload,
        }


class RunLedger:
    """Append-only JSONL ledger for durable, replayable agent runs."""

    def __init__(self, path: Path, run_id: str):
        self.path = Path(path)
        self.run_id = str(run_id)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._step = 0

    def append(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> LedgerEvent:
        self._step += 1
        event = LedgerEvent(
            run_id=self.run_id,
            step=self._step,
            event_type=str(event_type),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            payload=dict(payload or {}),
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True, default=str) + "\n")
        return event

    def read(self) -> List[LedgerEvent]:
        events: List[LedgerEvent] = []
        if not self.path.exists():
            return events
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            events.append(LedgerEvent(**payload))
        return events

    def summary(self) -> Dict[str, Any]:
        events = self.read()
        return {
            "run_id": self.run_id,
            "events": len(events),
            "event_types": [e.event_type for e in events],
            "last_step": events[-1].step if events else 0,
        }
