import numpy as np
import functools as ft
from dataclasses import dataclass
from typing import List, Callable, Optional

# COMPAT
if hasattr(ft, 'cache'):
    cache = ft.cache
else:
    cache = ft.lru_cache


@dataclass(frozen=True, order=True)
class Label:
    text: str


@dataclass(frozen=True, order=True)
class Token:
    text: str
    bbox: List[int]


@dataclass(frozen=True, order=True)
class Menu:
    text: str
    function: Optional[Callable] = None


class BBox:
    TWO_CORNERS = 0
    POLYGON = 1
    """
    The interface for bounding box, support two format
    - Four corner: [x1, x2, y1, y2]
    - Polygon: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    """

    def __init__(self, bbox):
        self.bbox = bbox

    @property
    @cache
    def kind(self):
        if isinstance(self.bbox[0], (int, float)):
            return BBox.TWO_CORNERS
        else:
            return BBox.POLYGON

    @property
    @cache
    def poly(self):
        if self.kind == BBox.TWO_CORNERS:
            x1, x2, y1, y2 = self.bbox
            return [[x1, y1],
                    [x2, y1],
                    [x2, y2],
                    [x2, y1]]
        else:
            return self.bbox

    @property
    @cache
    def xy(self):
        if self.kind == BBox.TWO_CORNERS:
            return self.bbox
        else:
            # Not really accurate
            # but this is only needed for displaying, so...
            x = [pt[0] for pt in self.bbox]
            y = [pt[1] for pt in self.bbox]
            x1 = min(x)
            x2 = max(x)
            y1 = min(y)
            y2 = max(y)
            return x1, x2, y1, y2

    @property
    @cache
    def center(self):
        x1, x2, y1, y2 = self.xy
        return (x1 + x2) / 2, (y1 + y2) / 2

    @property
    @cache
    def center_x(self):
        x1, x2, y1, y2 = self.xy
        return (x1 + x2) / 2

    @property
    @cache
    def center_y(self):
        x1, x2, y1, y2 = self.xy
        return (y1 + y2) / 2

    @property
    @cache
    def width(self):
        x1, x2, y1, y2 = self.xy
        return x1 - x2

    @property
    @cache
    def height(self):
        x1, x2, y1, y2 = self.xy
        return y2 - y1

    @property
    @cache
    def hash(self):
        return '-'.join(map(str, self.xy))


class Graph:
    def __init__(s, labels, texts, bboxes, adj=None, text_first=True):
        if not isinstance(bboxes[0], str):
            bboxes = [b.hash for b in bboxes]
        s.labels = [Label(label) for label in labels]
        s.tokens = [Token(text, bbox) for (text, bbox) in zip(texts, bboxes)]
        s.edges = []

        if adj is None:
            return

        if isinstance(adj, list):
            adj = np.array(adj)

        ntext = len(texts)
        nlabels = len(labels)
        # If the text is placed first on the
        # imported adjacency matrix
        if text_first:
            adj_text = adj[:ntext, :]
            adj_label = adj[ntext:, :]
        else:
            adj_text = adj[nlabels:, :]
            adj_label = adj[:nlabels, :]

        for (i, j) in zip(*np.where(adj_text == 1)):
            s.edges.append((s.tokens[i], s.tokens[j]))
        for (i, j) in zip(*np.where(adj_label == 1)):
            s.edges.append((s.labels[i], s.tokens[j]))

    def update_labels(self, labels):
        self.labels = [Label(label) for label in labels]
        self.edges = [(u, v) for (u, v) in self.edges
                      if (u in self.labels or u in self.tokens)
                      and (v in self.labels or v in self.tokens)]

    def toggle_edge(self, i, j):
        nodes = self.nodes
        assert i in nodes
        assert j in nodes
        e = (i, j)
        if e in self.edges:
            self.edges.remove(e)
        else:
            self.edges.append(e)

    def remove_edge(self, i, j):
        if (i, j) in self.edges:
            self.edges.remove((i, j))

    @property
    def nodes(s):
        return s.labels + s.tokens

    @property
    def nlabels(s):
        return len(s.labels)

    @property
    def nedges(s):
        return len(s.edges)

    @property
    def ntokens(s):
        return len(s.tokens)

    @property
    def nnodes(s):
        return len(s.tokens) + len(s.labels)

    @property
    def adj(self):
        nlabels = len(self.labels)
        ntokens = len(self.tokens)
        adj_tokens = np.zeros((ntokens, ntokens), dtype=int)
        adj_labels = np.zeros((nlabels, ntokens), dtype=int)

        for (i, l) in enumerate(self.labels):
            for (j, t) in enumerate(self.tokens):
                if (l, t) in self.edges:
                    adj_labels[i, j] = True

        for (i, u) in enumerate(self.tokens):
            for (j, v) in enumerate(self.tokens):
                if (u, v) in self.edges:
                    adj_tokens[i, j] = True

        return np.concatenate([adj_labels, adj_tokens], axis=0)


if __name__ == "__main__":
    a = Token('asdsa', [1, 2, 1, 1])
    b = Token('what', [2, 2, 1, 1])
    print([b, a])

    print(sorted([a, b]))
