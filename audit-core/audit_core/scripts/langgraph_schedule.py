from __future__ import annotations

from typing import Any


def run_langgraph(*, nodes: dict[str, Any], edges: list[tuple[str, str]], start: str) -> dict[str, Any]:
    try:
        from langgraph.graph import StateGraph
    except Exception:
        return _run_sequential(nodes=nodes, order=_topo_like(start=start, edges=edges))

    class _State(dict):
        pass

    graph = StateGraph(_State)
    for name, fn in nodes.items():
        graph.add_node(name, fn)
    graph.set_entry_point(start)
    for a, b in edges:
        graph.add_edge(a, b)
    compiled = graph.compile()
    return dict(compiled.invoke({}))


def _run_sequential(*, nodes: dict[str, Any], order: list[str]) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for name in order:
        out = nodes[name](state)
        if isinstance(out, dict):
            state.update(out)
        else:
            state[name] = out
    return state


def _topo_like(*, start: str, edges: list[tuple[str, str]]) -> list[str]:
    order = [start]
    seen = {start}
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            if a in seen and b not in seen:
                order.append(b)
                seen.add(b)
                changed = True
    return order
