from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import pandas as pd

from tscfbench.agent.context import ArtifactRef
from tscfbench.agent.tokens import canonical_json_dumps, estimate_json_tokens, estimate_text_tokens

ManifestLike = Union[str, Path, Dict[str, Any]]


def _load_manifest(manifest: ManifestLike) -> Dict[str, Any]:
    if isinstance(manifest, dict):
        return manifest
    return json.loads(Path(manifest).read_text(encoding="utf-8"))


def _coerce_artifact_ref(obj: Dict[str, Any]) -> ArtifactRef:
    return ArtifactRef(
        id=str(obj["id"]),
        kind=str(obj["kind"]),
        path=str(obj["path"]),
        media_type=str(obj["media_type"]),
        bytes=int(obj["bytes"]),
        approx_tokens=int(obj["approx_tokens"]),
        summary=str(obj["summary"]),
    )


def iter_artifact_refs(manifest: ManifestLike) -> List[ArtifactRef]:
    payload = _load_manifest(manifest)
    refs: List[ArtifactRef] = []
    seen = set()
    for group in payload.get("artifacts", {}).values():
        for item in group or []:
            ref = _coerce_artifact_ref(item)
            if ref.id in seen:
                continue
            seen.add(ref.id)
            refs.append(ref)
    return refs


def list_artifacts(manifest: ManifestLike) -> List[Dict[str, Any]]:
    return [ref.to_dict() for ref in iter_artifact_refs(manifest)]


def resolve_artifact(
    manifest: ManifestLike,
    *,
    artifact_id: Optional[str] = None,
    kind: Optional[str] = None,
    path: Optional[str] = None,
) -> ArtifactRef:
    refs = iter_artifact_refs(manifest)
    if artifact_id is not None:
        for ref in refs:
            if ref.id == artifact_id:
                return ref
        raise KeyError(f"Artifact id not found: {artifact_id}")
    if path is not None:
        path_text = str(path)
        for ref in refs:
            if ref.path == path_text or Path(ref.path).name == path_text:
                return ref
        raise KeyError(f"Artifact path not found: {path}")
    if kind is not None:
        candidates = [ref for ref in refs if ref.kind == kind]
        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            raise KeyError(f"Artifact kind not found: {kind}")
        raise KeyError(f"Artifact kind is ambiguous: {kind}; candidates={[c.id for c in candidates]}")
    raise ValueError("Provide one of artifact_id, kind, or path")


def read_text_artifact(
    manifest: ManifestLike,
    *,
    artifact_id: Optional[str] = None,
    kind: Optional[str] = None,
    path: Optional[str] = None,
    offset_chars: int = 0,
    max_chars: int = 4000,
) -> Dict[str, Any]:
    ref = resolve_artifact(manifest, artifact_id=artifact_id, kind=kind, path=path)
    file_path = Path(ref.path)
    text = file_path.read_text(encoding="utf-8", errors="replace")
    start = max(0, int(offset_chars))
    limit = max(0, int(max_chars))
    snippet = text[start:start + limit]
    truncated = start + limit < len(text)
    return {
        "artifact": ref.to_dict(),
        "offset_chars": start,
        "max_chars": limit,
        "returned_chars": len(snippet),
        "total_chars": len(text),
        "truncated": truncated,
        "text": snippet,
        "token_estimate": estimate_text_tokens(snippet).to_dict(),
    }


def _coerce_rows(obj: Any) -> pd.DataFrame:
    if isinstance(obj, pd.DataFrame):
        return obj
    if isinstance(obj, list):
        return pd.DataFrame(obj)
    if isinstance(obj, dict):
        if all(isinstance(v, list) for v in obj.values()):
            return pd.DataFrame(obj)
        return pd.DataFrame([obj])
    raise TypeError(f"Unsupported JSON payload for tabular preview: {type(obj)!r}")


def preview_tabular_artifact(
    manifest: ManifestLike,
    *,
    artifact_id: Optional[str] = None,
    kind: Optional[str] = None,
    path: Optional[str] = None,
    rows: int = 8,
    columns: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    ref = resolve_artifact(manifest, artifact_id=artifact_id, kind=kind, path=path)
    file_path = Path(ref.path)
    if ref.media_type == "text/csv" or file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif ref.media_type == "application/json" or file_path.suffix.lower() == ".json":
        obj = json.loads(file_path.read_text(encoding="utf-8"))
        df = _coerce_rows(obj)
    else:
        raise ValueError(f"Artifact is not tabular: {ref.media_type}")

    if columns:
        keep = [c for c in columns if c in df.columns]
        if keep:
            df = df.loc[:, keep]
    head = df.head(max(1, int(rows))).copy()
    return {
        "artifact": ref.to_dict(),
        "rows_returned": int(len(head)),
        "total_rows": int(len(df)),
        "columns": list(df.columns),
        "preview": head.to_dict(orient="records"),
        "token_estimate": estimate_json_tokens(head.to_dict(orient="records")).to_dict(),
    }


def search_text_artifact(
    manifest: ManifestLike,
    *,
    query: str,
    artifact_id: Optional[str] = None,
    kind: Optional[str] = None,
    path: Optional[str] = None,
    max_hits: int = 8,
) -> Dict[str, Any]:
    ref = resolve_artifact(manifest, artifact_id=artifact_id, kind=kind, path=path)
    file_path = Path(ref.path)
    text = file_path.read_text(encoding="utf-8", errors="replace")
    needle = str(query).lower().strip()
    if not needle:
        raise ValueError("query must be non-empty")
    hits: List[Dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if needle in line.lower():
            hits.append({"line_no": line_no, "text": line[:400]})
            if len(hits) >= max(1, int(max_hits)):
                break
    return {
        "artifact": ref.to_dict(),
        "query": query,
        "hits": hits,
        "hit_count": len(hits),
        "token_estimate": estimate_json_tokens(hits).to_dict(),
    }


def summarize_manifest(manifest: ManifestLike) -> Dict[str, Any]:
    payload = _load_manifest(manifest)
    refs = iter_artifact_refs(payload)
    total_artifact_tokens = int(sum(r.approx_tokens for r in refs))
    files = payload.get("files", {})
    summary = {
        "schema_version": payload.get("schema_version"),
        "run_id": payload.get("run_id"),
        "n_artifacts": len(refs),
        "artifact_kinds": sorted({r.kind for r in refs}),
        "total_artifact_tokens": total_artifact_tokens,
        "files": files,
    }
    return summary


def artifact_catalog_text(manifest: ManifestLike) -> str:
    refs = iter_artifact_refs(manifest)
    lines = ["# Artifact catalog"]
    for ref in refs:
        lines.append(
            f"- {ref.kind}: id={ref.id} tokens≈{ref.approx_tokens} bytes={ref.bytes} path={Path(ref.path).name}"
        )
    return "\n".join(lines)
