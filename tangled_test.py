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
paper_dataset = ['baba', 'abba', 'abcabc', 'cbacba',
                 'abbbba', 'cbacbacba', 'abbba', 'babababc']
res = learn_ktest_union(paper_dataset, 3)
print(list(map(lambda x: x[1], res)))
