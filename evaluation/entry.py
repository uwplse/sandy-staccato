import subprocess
import sys
import os
import yaml
import tempfile

this_dir = os.path.realpath(os.path.dirname(sys.argv[0]))

eval_script = lambda s: os.path.join(this_dir, s)

projects = ["openfire", "jforum", "subsonic"]

for p in projects:
    with open(os.path.join(this_dir, p, "bug_db.yml"), 'w') as f:
        print >> f, '[]'

def compute_bug_statistics(res):
    total_bugs = 0
    total_fp = 0
    stats = {}
    for (p,st) in res.iteritems():
        project_bugs = len(st)
        project_fp = 0
        for (b_name, info) in st.iteritems():
            if info["type"] == "false positive":
                project_fp += 1
        stats[p] = {
            "reports": project_bugs,
            "fp": project_fp,
            "rate": float(project_fp) / project_bugs
        }
        total_bugs += project_bugs
        total_fp += project_fp
    stats["cumulative"] = {
        "reports": total_bugs,
        "fp": total_fp,
        "rate": float(total_fp) / total_bugs
    }
    return stats

def run_bug_finder():
    bug_results = {}
    for p in projects:
        project_dir = lambda f: os.path.join(this_dir, p, f)
        with open(eval_script("staccato_tests.log"), 'a') as out:
            subprocess.check_call(["python", eval_script("run_staccato.py"), project_dir("test_config.yml")], stdout = out)
            yaml_dump = subprocess.check_output(["python", eval_script("classify_bugs.py"), project_dir("bug_db.yml"), project_dir("bug_classification.yml"), "--yaml"], stderr = out)
            bug_results[p] = yaml.load(yaml_dump)
    return compute_bug_statistics(bug_results)

def toggle_test():
    f = tempfile.NamedTemporaryFile(delete = True)
    with open("/dev/null", "w") as null:
        o = subprocess.check_output(["python", eval_script("run_toggle_test.py"), f.name], stderr = null)
    return yaml.load(f)

with open(sys.argv[1], "w") as out:
    yaml.dump({
        "bug": run_bug_finder(),
        "toggle": toggle_test()
    }, out)
