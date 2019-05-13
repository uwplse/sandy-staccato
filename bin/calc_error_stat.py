from data_parsers import handlers
import sys

h = handlers[sys.argv[1]]

if sys.argv[1] == "openfire":
    (_, _, e1) = h(sys.argv[2])
    (_, _, e2) = h(sys.argv[3])
    print e2 - e1
else:
    (_, p1, e1) = h(sys.argv[2])
    (_, p2, e2) = h(sys.argv[3])
    p1_good_reqs = sum(map(lambda x: len(x), p1.itervalues()))
    p2_good_reqs = sum(map(lambda x: len(x), p2.itervalues()))
    base_rate = e1 / float(p1_good_reqs + e1)
    toggle_rate = e2 / float(p2_good_reqs + e2)
    print toggle_rate - base_rate
    
