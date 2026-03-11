from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from tscfbench.agent.tokens import estimate_text_tokens


@dataclass(frozen=True)
class RepoSymbol:
    kind: str
    name: str
    signature: str
    doc: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "kind": self.kind,
            "name": self.name,
            "signature": self.signature,
            "doc": self.doc,
        }


@dataclass(frozen=True)
class RepoMapEntry:
    path: str
    score: float
    symbols: List[RepoSymbol]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "score": self.score,
            "symbols": [s.to_dict() for s in self.symbols],
        }


def _iter_py_files(repo_root: Path, include_tests: bool = False) -> Iterable[Path]:
    excluded = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "dist", "build"}
    for path in repo_root.rglob("*.py"):
        if any(part in excluded for part in path.parts):
            continue
        if not include_tests and "tests" in path.parts:
            continue
        yield path


def _annotation_text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # noqa: BLE001
        return ""


def _args_signature(args: ast.arguments) -> str:
    pieces: List[str] = []
    defaults = list(args.defaults)
    default_start = len(args.args) - len(defaults)

    for idx, arg in enumerate(args.args):
        text = arg.arg
        if arg.annotation is not None:
            text += f": {_annotation_text(arg.annotation)}"
        if idx >= default_start:
            text += "=?"
        pieces.append(text)

    if args.vararg is not None:
        text = f"*{args.vararg.arg}"
        if args.vararg.annotation is not None:
            text += f": {_annotation_text(args.vararg.annotation)}"
        pieces.append(text)
    elif args.kwonlyargs:
        pieces.append("*")

    for kwarg, default in zip(args.kwonlyargs, args.kw_defaults):
        text = kwarg.arg
        if kwarg.annotation is not None:
            text += f": {_annotation_text(kwarg.annotation)}"
        if default is not None:
            text += "=?"
        pieces.append(text)

    if args.kwarg is not None:
        text = f"**{args.kwarg.arg}"
        if args.kwarg.annotation is not None:
            text += f": {_annotation_text(args.kwarg.annotation)}"
        pieces.append(text)

    return ", ".join(pieces)


def _doc_line(node: ast.AST) -> str:
    doc = ast.get_docstring(node) or ""
    doc = doc.strip().splitlines()[0] if doc.strip() else ""
    return doc[:120]


def _extract_symbols(path: Path) -> List[RepoSymbol]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []

    out: List[RepoSymbol] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(
                RepoSymbol(
                    kind="function",
                    name=node.name,
                    signature=f"{node.name}({_args_signature(node.args)})",
                    doc=_doc_line(node),
                )
            )
        elif isinstance(node, ast.ClassDef):
            methods: List[str] = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not child.name.startswith("_"):
                    methods.append(child.name)
            suffix = f" methods={methods[:4]}" if methods else ""
            out.append(
                RepoSymbol(
                    kind="class",
                    name=node.name,
                    signature=f"class {node.name}{suffix}",
                    doc=_doc_line(node),
                )
            )
    return out


def _score(path: Path, symbols: Sequence[RepoSymbol], query: Optional[str]) -> float:
    if not query:
        return 0.0
    tokens = [t for t in re.split(r"[^a-zA-Z0-9_]+", query.lower()) if t]
    path_text = str(path).lower()
    score = 0.0
    for token in tokens:
        if token in path_text:
            score += 3.0
        for sym in symbols:
            if token in sym.name.lower():
                score += 1.5
            if sym.doc and token in sym.doc.lower():
                score += 0.5
    return score


def build_repo_map(
    repo_root: Path,
    query: Optional[str] = None,
    max_files: int = 12,
    max_symbols_per_file: int = 8,
    include_tests: bool = False,
) -> List[RepoMapEntry]:
    repo_root = Path(repo_root)
    entries: List[RepoMapEntry] = []
    for path in _iter_py_files(repo_root, include_tests=include_tests):
        symbols = _extract_symbols(path)
        if not symbols:
            continue
        rel = path.relative_to(repo_root).as_posix()
        entries.append(
            RepoMapEntry(
                path=rel,
                score=_score(path, symbols, query),
                symbols=symbols[:max_symbols_per_file],
            )
        )

    if query:
        entries = sorted(entries, key=lambda e: (-e.score, e.path))
    else:
        entries = sorted(entries, key=lambda e: e.path)
    return entries[:max_files]


def build_repo_map_text(
    repo_root: Path,
    query: Optional[str] = None,
    max_files: int = 12,
    max_symbols_per_file: int = 8,
    include_tests: bool = False,
    include_token_footer: bool = True,
) -> str:
    entries = build_repo_map(
        repo_root=repo_root,
        query=query,
        max_files=max_files,
        max_symbols_per_file=max_symbols_per_file,
        include_tests=include_tests,
    )
    lines: List[str] = []
    lines.append(f"# Repo map for query: {query}" if query else "# Repo map")
    for entry in entries:
        lines.append(f"{entry.path} [score={entry.score:.1f}]" if query else entry.path)
        for sym in entry.symbols:
            doc = f" — {sym.doc}" if sym.doc else ""
            lines.append(f"  - {sym.kind}: {sym.signature}{doc}")
    text = "\n".join(lines)
    if include_token_footer:
        est = estimate_text_tokens(text)
        text += f"\n\n# approx_tokens={est.approx_tokens}"
    return text
