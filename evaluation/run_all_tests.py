import sys
import subprocess
import os, os.path
import yaml

num_iterations = 3
is_paper_test = False

if len(sys.argv) > 1 and sys.argv[1] == '--full':
    num_iterations = 5
    is_paper_test = True


sub_projects = [ "openfire", "subsonic", "jforum" ]

this_dir = os.path.realpath(os.path.dirname(sys.argv[0]))

perf_environ = dict(os.environ)
perf_environ["PYTHONPATH"] = this_dir

def execute_test_run(project, is_mem):
    test_file = os.path.join(this_dir, project, "performance_test.py")
    call = ["python", test_file ]
    if is_paper_test:
        call.append("--full")
    if is_mem:
        call.append("mem")
    out = subprocess.check_output(call, env = perf_environ)
    res = out.split()
    assert len(res) == 2
    return (res[0], res[1])

def run_test(project, is_mem):
    inst_ret = []
    base_ret = []
    for i in range(0, num_iterations):
        (inst, b) = execute_test_run(project, is_mem)
        inst_ret.append(inst)
        base_ret.append(b)
    return (inst_ret, base_ret)

output = {"runtime": {}, "memory": {}}

for project in sub_projects:
    for i in [False, True]:
        is_mem_pass = i
        st = "memory" if is_mem_pass else "runtime"
        print "Testing %s %s overhead" % (project, st)
        (inst, base) = run_test(project, is_mem_pass)
        target_out = None
        if is_mem_pass:
            target_out = output["memory"]
        else:
            target_out = output["runtime"]
        target_out[project] = {
            "base": base,
            "inst": inst
        }

with open(os.path.join(this_dir, "data.yml"), 'w') as f:
    yaml.dump(output, f)

print "Done"
