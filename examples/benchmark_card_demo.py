from __future__ import annotations

from tscfbench.guidebook import benchmark_cards

for card in benchmark_cards():
    print(card["id"], "->", card["title"])
