"""Exact Boolean relay support, supplied by an enumerated reduced kernel."""

from dataclasses import dataclass
import numpy as np
from .measurements import finite
from .spectral import reachable


@dataclass(frozen=True)
class ShockSupport:
    admitted: bool
    route: str
    relay_cycle: tuple[int, ...] = ()


def relay_graph(survival_support, birth_support):
    """Relay i->j: parent i survives zero or more steps, then produces j.

    Nodes carry phase, age, welfare and entrant type as needed. Supports
    must include shocks at lowest admissible welfare. A birth by a dying
    parent is a birth edge without requiring a same-step survivor edge.
    Edges must be exact positive support, not Monte Carlo observations.
    """
    s, b = np.asarray(survival_support), np.asarray(birth_support)
    if s.dtype != bool or b.dtype != bool or s.ndim != 2 or s.shape[0] != s.shape[1] or s.shape != b.shape or not len(s):
        raise ValueError("matching nonempty Boolean square support matrices required")
    closure = reachable(s)
    return np.any(closure[:, :, None] & b[None, :, :], axis=1)


def find_cycle(graph, initial_nodes):
    graph = np.asarray(graph, bool)
    roots = tuple(initial_nodes)
    if not roots or any(i < 0 or i >= len(graph) for i in roots):
        raise ValueError("valid initial support required")
    reach = reachable(graph)
    allowed = np.any(reach[list(roots)], axis=0)
    # Iterative DFS avoids recursion-depth dependence on declared grid size.
    color = [0] * len(graph)
    for root in np.flatnonzero(allowed):
        if color[root]:
            continue
        path = [int(root)]
        color[root] = 1
        stack = [iter(np.flatnonzero(graph[root] & allowed))]
        while stack:
            j = next(stack[-1], None)
            if j is None:
                color[path.pop()] = 2
                stack.pop()
            elif color[j] == 1:
                return tuple(path[path.index(j):] + [int(j)])
            elif color[j] == 0:
                color[j] = 1
                path.append(int(j))
                stack.append(iter(np.flatnonzero(graph[j] & allowed)))
    return ()


def shock_support(removal_fraction, welfare_loss, certified_margin, *, survival_support=None, birth_support=None, initial_nodes=None):
    removal = finite(removal_fraction, "removal_fraction", 0, 1)
    loss = finite(welfare_loss, "welfare_loss", 0)
    margin = finite(certified_margin, "certified_margin", 0)
    if removal == 1:
        return ShockSupport(False, "total removal")
    if loss <= margin:
        return ShockSupport(True, "certified fertility margin")
    if survival_support is None or birth_support is None or initial_nodes is None:
        raise ValueError("beyond-margin schedules require exact phase-aware support")
    graph = relay_graph(survival_support, birth_support)
    cycle = find_cycle(graph, initial_nodes)
    return ShockSupport(bool(cycle), "relay cycle" if cycle else "no relay cycle", cycle)
