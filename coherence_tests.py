from operator import itemgetter
import argparse
parser = argparse.ArgumentParser(description='Learn a k-test union from a dataset')
parser.add_argument('dataset', type=str)
parser.add_argument('method', type=str, choices=['graph', 'de_facto'])
args = parser.parse_args()

if args.method == 'graph':
    from tangled_ktestable import learn_ktest_union
else:
    from tangled_ktestable_v2 import learn_ktest_union

with open(args.dataset) as datasetfile:
    dataset = [line.rstrip('\n') for line in datasetfile]

union = learn_ktest_union(dataset, 3)
clusters = list(map(itemgetter(1), union))
print(clusters)
print(len(clusters))
