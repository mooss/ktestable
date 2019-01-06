from tangled_ktestable import ktestable, learn_ktest_union

examples = {
    'z3': ({'ab'}, {'bc'}, {'abc', 'bca', 'cab'}, {}),
    'z4': ({'cb'}, {'ba'}, {'cba', 'bac', 'acb'}, {}),
    'z5': ({'ab'}, {'ba'}, {'abb', 'bbb', 'bba'}, {}),
    'z7': ({'ab'}, {'ba'}, {'abb', 'bbb', 'bba'}, {}),
}

instances = {iden: ktestable(*params) for iden, params in examples.items()}

print(instances['z5'].is_union_consistent_with(instances['z7']))
print(instances['z3'].is_union_consistent_with(instances['z4']))
print(instances['z3'].is_union_consistent_with(instances['z7']))

print()
print(ktestable.from_example('baba', 3).is_union_consistent_with(ktestable.from_example('babababc', 3)))

with open('dataset/paper.txt') as datasetfile:
    dataset = [line.rstrip('\n') for line in datasetfile]

res = learn_ktest_union(dataset, 3)
clusters = list(map(lambda x: x[1], res))
print(clusters)
print(len(clusters))
