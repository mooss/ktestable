from collections import namedtuple, defaultdict

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

    def is_union_consistent_with(self, other):
        red_infixes = self.infixes - other.infixes
        red_start = self.prefixes - other.prefixes
        red_start.update(inf[1:] for inf in red_infixes)
        red_stop = self.suffixes - other.suffixes
        red_stop.update(inf[:-1] for inf in red_infixes)
        
        blue_infixes = other.infixes - self.infixes
        blue_start = other.prefixes - self.prefixes
        blue_start.update(inf[1:] for inf in blue_infixes)
        blue_stop = other.suffixes - self.suffixes
        blue_stop.update(inf[:-1] for inf in blue_infixes)
    
        if blue_start & red_stop or red_start & blue_stop:
            return False
    
        white_infixes = self.infixes & other.infixes
        de_facto_red = string_transitive_closure(red_start, white_infixes)
        de_facto_blue = string_transitive_closure(blue_start, white_infixes)
        
        de_facto_red = {el[1:] for el in de_facto_red}
        de_facto_blue = {el[1:] for el in de_facto_blue}
        
        return not(de_facto_blue & red_stop) and not(de_facto_red & blue_stop)

def string_transitive_closure(starting_components, infixes):
    prefdict = defaultdict(set)
    for inf in infixes:
        prefdict[inf[:-1]].add(inf)

    closure = set()
    for pref in starting_components:
        if pref in prefdict:
            closure.update(prefdict.pop(pref))

    result = set()
    while closure:
        el = closure.pop()
        result.add(el)
        if el[1:] in prefdict:
           closure.update(prefdict.pop(el[1:]))
    return result

def learn_ktest_union(examples, k):
    ktest_vectors = [ktestable.from_example(ex, k) for ex in examples]
    indexes = list(range(len(ktest_vectors)))
    already_merged = [False] * len(ktest_vectors)
    
    distance_link = namedtuple('d', 'neighbours left')
    distance_chain = []
    
    for left in range(0, len(ktest_vectors) - 1):
        neighbours = []
        for right in range(left + 1, len(ktest_vectors)):
            neigh = (ktest_vectors[left].distance(ktest_vectors[right]), right)
            neighbours.append(neigh)
        neighbours.sort()
        distance_chain.append(distance_link(neighbours=neighbours, left=left))
    distance_chain.sort()

    while True:
        while True:
            if len(distance_chain) == 0:
                return [(ktest_vectors[x], indexes[x])
                        for x, merged in enumerate(already_merged) if not merged]
        
            left, (dist, right) = distance_chain[0].left, distance_chain[0].neighbours[0]
            if not already_merged[right] and\
               ktest_vectors[left].is_union_consistent_with(ktest_vectors[right]):
                break
        
            del distance_chain[0].neighbours[0]
            if len(distance_chain[0].neighbours) == 0:
                del distance_chain[0]
        
            distance_chain.sort()

        indexes.append((indexes[left], indexes[right], dist))
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
