"""Преобразование графа в PlantUML и ASCII."""

def plantuml(graph):
    """Объявить вершины и направленные рёбра с безопасными псевдонимами."""
    aliases = {name: f"p{i}" for i, name in enumerate(graph.edges)}
    lines = ["@startuml", "left to right direction"]
    missing = set(graph.missing)
    for name, alias in aliases.items():
        label = name + (" (missing)" if name in missing else "")
        lines.append(f'component "{label}" as {alias}')
    cycles = set(graph.back_edges)
    for name, children in graph.edges.items():
        for child in children:
            tail = " : cycle" if (name, child) in cycles else ""
            lines.append(f"{aliases[name]} --> {aliases[child]}{tail}")
    lines.append("@enduml")
    return "\n".join(lines)


def child_frames(graph, node, prefix):
    """Подготовить стек потомков в порядке печати слева направо."""
    names = graph.edges[node]
    return [
        (child, prefix, position == len(names))
        for position, child in reversed(list(enumerate(names, 1)))
    ]


def ascii_tree(graph):
    """Развернуть граф в дерево со ссылками на повторные вершины."""
    lines = [graph.root]
    seen = {graph.root}
    missing = set(graph.missing)
    stack = child_frames(graph, graph.root, "")
    while stack:
        node, prefix, last = stack.pop()
        connector = "`-- " if last else "|-- "
        repeated = node in seen
        suffix = " [see above]" if repeated else ""
        if node in missing:
            suffix += " [missing]"
        lines.append(prefix + connector + node + suffix)
        if not repeated:
            seen.add(node)
            indent = "    " if last else "|   "
            stack.extend(child_frames(graph, node, prefix + indent))
    return "\n".join(lines)
