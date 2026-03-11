from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Dict


def canonical_json_dumps(obj: Any, pretty: bool = False) -> str:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        default=str,
    )


@dataclass(frozen=True)
class TokenEstimate:
    chars: int
    bytes: int
    approx_tokens: int
    method: str = "chars_div_4"

    def fits(self, limit: int) -> bool:
        return self.approx_tokens <= int(limit)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chars": self.chars,
            "bytes": self.bytes,
            "approx_tokens": self.approx_tokens,
            "method": self.method,
        }


@dataclass(frozen=True)
class TokenBudget:
    input_limit: int = 8000
    reserve_for_output: int = 2000
    reserve_for_instructions: int = 1000

    @property
    def usable_context_tokens(self) -> int:
        return max(0, int(self.input_limit) - int(self.reserve_for_output) - int(self.reserve_for_instructions))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_limit": int(self.input_limit),
            "reserve_for_output": int(self.reserve_for_output),
            "reserve_for_instructions": int(self.reserve_for_instructions),
            "usable_context_tokens": int(self.usable_context_tokens),
        }


def estimate_text_tokens(text: str) -> TokenEstimate:
    text = text or ""
    chars = len(text)
    byte_count = len(text.encode("utf-8"))
    approx = int(math.ceil(chars / 4.0)) if chars else 0
    return TokenEstimate(chars=chars, bytes=byte_count, approx_tokens=approx)


def estimate_json_tokens(obj: Any, pretty: bool = False) -> TokenEstimate:
    return estimate_text_tokens(canonical_json_dumps(obj, pretty=pretty))
