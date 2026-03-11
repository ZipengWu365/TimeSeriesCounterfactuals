from __future__ import annotations

from tscfbench.guidebook import recommend_start_path

payload = recommend_start_path(persona="applied researcher", task_family="panel", environment="notebook", goal="own data")
print(payload["primary_recipe"]["title"])
print(payload["recommended_cli"][:2])
