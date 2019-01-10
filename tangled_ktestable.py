from collections import namedtuple
import networkx as nx

def ktest_tuple(example, k):
    if len(example) < k - 1:
        prefixes = set()
        suffixes = set()
        shorts = {example}
    else:
        prefixes = {example[:k-1]}
        suffixes = {example[-k+1:]}
        shorts = prefixes & suffixes

    infixes = {example[i:i+k] for i in range(0, len(example) - k + 1)}
    return (prefixes, suffixes, infixes, shorts)


class ktestable(object):
    def __init__(self, prefixes, suffixes, infixes, shorts, k=None):
        self.k = len(next(iter(infixes))) if k is None else k
        self.prefixes = prefixes
        self.suffixes = suffixes
        self.infixes = infixes
        self.shorts = shorts
        self.ensure_correct_definition()

    @classmethod
    def from_example(cls, example, k):
        return cls(*ktest_tuple(example, k), k)

    def ensure_correct_definition(self):
        def same_length(collection, reference_length):
            return all(map(lambda x: len(x) == reference_length, collection))
    
        errors = []
        if not same_length(self.prefixes, self.k - 1):
            errors.append('incorrect prefix length')
        if not same_length(self.suffixes, self.k - 1):
            errors.append('incorrect suffix length')
        if not same_length(self.infixes, self.k):
            errors.append('incorrect infix length')
        if not all(map(lambda x: len(x) < self.k, self.shorts)):
            errors.append('incorrect short string length')
    
        presuffixes = self.prefixes & self.suffixes
        shorts_len_k = set(filter(lambda x: len(x) == self.k - 1, self.shorts))
        if presuffixes != shorts_len_k:
            errors.append('short strings conditions not satisfied')
    
        if len(errors) >0:
            raise ValueError(', '.join(errors).capitalize() + '.')

    def ensure_compatibility(self, other):
        if self.k != other.k:
            raise ValueError('Incompatible k-test vectors: length mismatch (%d != %d)' %
                             (self.k, other.k))

    def union(self, other):
        self.ensure_compatibility(other)
        prefixes = self.prefixes | other.prefixes
        suffixes = self.suffixes | other.suffixes
        infixes = self.infixes | other.infixes
        shorts = self.shorts | other.shorts |\
            (self.prefixes & other.suffixes) |\
            (self.suffixes & other.prefixes)
        return ktestable(prefixes, suffixes, infixes, shorts, k=self.k)

    def intersection(self, other):
        self.ensure_compatibility(other)
        prefixes = self.prefixes & other.prefixes
        suffixes = self.suffixes & other.suffixes
        infixes = self.infixes & other.infixes
        shorts = self.shorts & other.shorts
        return ktestable(prefixes, suffixes, infixes, shorts, k=self.k)

    def symmetric_difference(self, other):
        self.ensure_compatibility(other)
        prefixes = self.prefixes ^ other.prefixes
        suffixes = self.suffixes ^ other.suffixes
        infixes = self.infixes ^ other.infixes
        shorts = self.shorts ^ other.shorts ^\
            (self.prefixes & other.suffixes) ^\
            (self.suffixes & other.prefixes)
        return ktestable(prefixes, suffixes, infixes, shorts, k=self.k)

    def __or__(self, other):
        return self.union(other)
    
    def __and__(self, other):
        return self.intersection(other)
    
    def __xor__(self, other):
        return self.symmetric_difference(other)

    def cardinality(self):
        return len(self.prefixes) + len(self.suffixes) + len(self.infixes) +\
            sum(map(lambda x: 1 if len(x) < self.k - 1 else 0, self.shorts))
    
    def __len__(self):
        return self.cardinality()

    def distance(self, other):
        return len(self ^ other)

    def consistency_graph(self, other):
        prefixes = {'P' + el for el in self.prefixes | other.prefixes}
        suffixes = {'S' + el for el in self.suffixes | other.suffixes}
        infixes = {el for el in self.infixes | other.infixes}
    
        edges = {(pre, inf) for pre in prefixes for inf in infixes
                 if pre[1:] == inf[:-1]}
        edges.update({(left, right) for left in infixes for right in infixes
                      if left[1:] == right[:-1]})
        edges.update({(inf, suf) for inf in infixes for suf in suffixes
                      if inf[1:] == suf[1:]})
    
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        return graph

    def is_union_consistent_with(self, other):
        reds = {'P' + el for el in self.prefixes - other.prefixes} |\
            {'S' + el for el in self.suffixes - other.suffixes} |\
            self.infixes - other.infixes
        blues = {'P' + el for el in other.prefixes - self.prefixes} |\
            {'S' + el for el in other.suffixes - self.suffixes} |\
            other.infixes - self.infixes
        
        graph = self.consistency_graph(other)
        closure = nx.algorithms.dag.transitive_closure(graph)
        red_reachable = {neighbour for red in reds if red in closure for neighbour in closure.adj[red]}
        blue_reachable = {neighbour for blue in blues if blue in closure for neighbour in closure.adj[blue]}
    
        return red_reachable.isdisjoint(blues) and blue_reachable.isdisjoint(reds)

def learn_ktest_union(examples, k):
    ktest_vectors = [ktestable.from_example(ex, k) for ex in examples]
    indexes = list(range(len(ktest_vectors)))
    already_merged = [False] * len(ktest_vectors)
    
    distance_link = namedtuple('d', 'neighbours left')
    distance_chain = []
    
    for left in range(0, len(ktest_vectors) - 1):
        neighbours = []
        for right in range(left + 1, len(ktest_vectors)):
            neighbours.append((ktest_vectors[left].distance(ktest_vectors[right]), right))
        neighbours.sort()
        distance_chain.append(distance_link(neighbours=neighbours, left=left))
    distance_chain.sort()

    while True:
        while True:
            left, (dist, right) = distance_chain[0].left, distance_chain[0].neighbours[0]
            if not already_merged[right] and\
               ktest_vectors[left].is_union_consistent_with(ktest_vectors[right]):
                break
        
            del distance_chain[0].neighbours[0]
            if len(distance_chain[0].neighbours) == 0:
                del distance_chain[0]
                if len(distance_chain) == 0:
                    return [(ktest_vectors[x], indexes[x])
                            for x, merged in enumerate(already_merged) if not merged]
        
            distance_chain.sort()

        indexes.append((indexes[left], indexes[right]))
        ktest_vectors.append(ktest_vectors[left] | ktest_vectors[right])
        already_merged.append(False)
        already_merged[left] = already_merged[right] = True

        del distance_chain[0]
        for i in range(len(distance_chain)):
            if distance_chain[i].left == right:
                del distance_chain[i]
                break

        neighbours = []
        for right, merged in enumerate(already_merged[:-1]):
            if not merged:
                neighbours.append((ktest_vectors[-1].distance(ktest_vectors[right]), right))
        
        neighbours.sort()
        distance_chain.append(distance_link(neighbours=neighbours, left=len(ktest_vectors) - 1))
        distance_chain.sort()
