import subprocess
import re
import os, os.path
import sys

this_dir = os.path.realpath(os.path.dirname(sys.argv[0]))


diff_line = re.compile(r'^[- +]')
context_line = re.compile(r'^(---|\+\+\+)')
import_line = re.compile(r'^\s*import')

check = 0
propagation = 0

def count_lines_in_path(file_name):
    global check
    global propagation
    lines_changed = 0
    with open(file_name, 'r') as f:
        for l in f:
            if re.match(diff_line, l) is None:
                continue
            if re.match(context_line, l) is not None:
                continue
            # context line
            if l.startswith(" "):
                continue
            if l.find('@StaccatoCheck') != -1:
                check += 1
            if l.find('@StaccatoProp') != -1:
                propagation += 1
            l = l[1:]
            l = l.strip()
            if len(l) == 0:
                continue
            if re.match(import_line, l) is not None:
                continue
            lines_changed += 1
    return lines_changed

output_map = {}

def count_lines_in_project(p):
    output_map[p] = {}
    project_dir = os.path.join(this_dir, p, "patches")
    patch_files = os.listdir(project_dir)
    for pf in patch_files:
        assert pf.endswith(".patch")
        cat = pf[:-len(".patch")]
        output_map[p][cat] = count_lines_in_path(os.path.join(project_dir, pf))

for p in ["subsonic", "openfire", "jforum"]:
    count_lines_in_project(p)

output_order = [
    "annotation",
    "flowchange", 
    "update",
    "bugfix",
    "confabs"
]

print "Project | Annot. | Flow | Repair CB | Bug-Fixes | Conf-Abs. | Total"

for p in ["openfire", "jforum","subsonic"]:
    p_map = output_map[p]
    p_counts = [ p_map[o] if o in p_map else 0 for o in output_order ]
    total = sum(p_counts)
    p_counts.append(total)
    print p + " | " + " | ".join([ str(c) for c in p_counts])

print "Total check: " + str(check)
print "Total propagation: " + str(propagation)
