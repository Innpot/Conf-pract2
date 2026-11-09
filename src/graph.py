"""Итеративный DFS по достижимым зависимостям."""

from dataclasses import dataclass


@dataclass
class Graph:
    """Вершины с рёбрами, обратные рёбра DFS и отсутствующие записи."""

    root: str
    edges: dict[str, tuple[str, ...]]
    back_edges: list[tuple[str, str]]
    missing: list[str]
    postorder: list[str]


def visit(graph, index, name, exclude):
    """Зарегистрировать вершину и отфильтровать исходящие рёбра."""
    if name not in index:
        graph.missing.append(name)
    graph.edges[name] = tuple(
        child for child in index.get(name, ())
        if not exclude or exclude not in child
    )
    return name, iter(graph.edges[name])


def build_graph(index, root, exclude=""):
    """Обойти только достижимые вершины; не входить в цикл повторно."""
    if root not in index:
        raise ValueError(f"Пакет {root} не найден в индексе")
    graph = Graph(root, {}, [], [], [])
    active = {root}
    stack = [visit(graph, index, root, exclude)]
    while stack:
        parent, children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            active.remove(parent)
            graph.postorder.append(parent)
        elif child in active:
            graph.back_edges.append((parent, child))
        elif child not in graph.edges:
            active.add(child)
            stack.append(visit(graph, index, child, exclude))
    return graph
