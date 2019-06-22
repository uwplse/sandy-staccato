import time
import subprocess
import os
import os.path
import eval_tools
import sys
import tempfile
import yaml

THIS_DIR = os.path.realpath(os.path.dirname(sys.argv[0]))

def do_tomcat_test(project, jmx_file, iterations):
    subprocess.check_call(["sudo", os.path.join(THIS_DIR, "deploy_wrapper"), project, "base"])
    rspec = eval_tools.RunSpec(False, None, os.path.join(THIS_DIR, project))
    print "done toggle deploy"
    toggle_proc = subprocess.Popen(["python", os.path.join(THIS_DIR, "toggle.py"), "tomcat", str(iterations)])
    print "spawned toggle"
    t1 = time.time()
    (jm_proc, cont) = eval_tools.get_jmeter_proc(rspec, jmx_file, "toggle", 702368, 550)
    print "started jmeter"
    toggle_proc.wait()
    t2 = time.time()
    print "toggle done???"
    print "shutting down jmeter"
    subprocess.check_call(["bash", "/home/staccato/apache-jmeter-2.12/bin/shutdown.sh"])
    print "waiting for jmeter"
    jm_proc.wait()
    toggle_file = cont()
   
    subprocess.check_call(["sudo", os.path.join(THIS_DIR, "deploy_wrapper"), project, "base"])
    (jm_proc, b_cont) = eval_tools.get_jmeter_proc(rspec, jmx_file, "baseline", 702368, 550)
    time.sleep(t2 - t1)
    subprocess.check_call(["bash", "/home/staccato/apache-jmeter-2.12/bin/shutdown.sh"])
    jm_proc.wait()
    print "successfull ran base"
    print "killing tomcat"
    subprocess.check_call(["sudo", os.path.join(THIS_DIR, "tomcat_control"), "shutdown"])
    return (b_cont(), toggle_file)

def run_tsung(scenario, data_dir):
    output_dir = os.path.join(THIS_DIR, "openfire", "data", data_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print "running tsung"
    tsung_proc = subprocess.Popen(["tsung", "-f", scenario, "-l", output_dir, "start"])
    def continuation():
        ret = tsung_proc.wait()
        if ret != 0:
            print "Tsung failed with exit code: %d" % ret
            sys.exit(10)
        l = [ d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d)) ]
        l.sort()
        data_dir = l[-1]
        subprocess.check_call(["perl", "/usr/lib/tsung/bin/tsung_stats.pl",  "--stat", "./tsung.log"], cwd = os.path.join(output_dir,data_dir))
        return os.path.realpath(os.path.join(output_dir,data_dir, "data"))
    return tsung_proc, continuation

def start_of_and_wait():
    log_file = "/tmp/of_test.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    proc = subprocess.Popen(["bash", os.path.join(THIS_DIR, "openfire", "deploy_of.sh"), "base", log_file])
    import wait_for_of
    wait_for_of.wait_for_openfire(proc, log_file)

tsung_file = "/home/staccato/staccato/evaluation/openfire/tsung-chat-update-mini.xml"

def do_openfire_test(tsung_file, iterations):
    sys.path.append(os.path.join(THIS_DIR, "openfire"))
    start_of_and_wait()
    toggle_proc = subprocess.Popen(["python", os.path.join(THIS_DIR, "toggle.py"), "openfire", str(iterations), "/home/staccato/evaluation-programs/openfire_orig/target/openfire/bin/openfire.sh"])
    t1 = time.time()
    (tproc, cont) = run_tsung(tsung_file, "toggle")
    toggle_proc.wait()
    t2 = time.time()
    subprocess.check_call(["tsung", "stop"])
    toggle_dir = cont()
    subprocess.check_call(["bash", os.path.join(THIS_DIR, "openfire", "kill_of.sh")])
    
    start_of_and_wait()
    (proc, cont) = run_tsung(tsung_file, "baseline")
    time.sleep(t2 - t1)
    subprocess.check_call(["tsung", "stop"])
    baseline_dir = cont()
    return (baseline_dir, toggle_dir)

iterations = 10

subprocess.check_call(["bash", os.path.join(THIS_DIR, "openfire/kill_of.sh")])
subprocess.check_call(["sudo", os.path.join(THIS_DIR, "tomcat_control"), "shutdown"])

ss_result = do_tomcat_test("subsonic", "/home/staccato/staccato/evaluation/subsonic/ss_test2_stateless.jmx", iterations)
jf_result =  do_tomcat_test("jforum", "/home/staccato/staccato/evaluation/jforum/forum_test_stateless.jmx", iterations)
of_result = do_openfire_test(tsung_file, iterations)

print ss_result
print jf_result
print of_result

tf = tempfile.NamedTemporaryFile(delete = True)


yaml.dump({
    "runtime": {
        "subsonic": {
            "base": [ ss_result[0] ],
            "inst": [ ss_result[1] ]
        },
        "jforum": {
            "base": [ jf_result[0] ],
            "inst": [ jf_result[1] ]
        },
        "openfire": {
            "base": [ of_result[0] ],
            "inst": [ of_result[1] ]
        }
    }
}, tf)

print tf.name

def get_slowdown(p_name):
    with open("/dev/null", "w") as null:
        val = subprocess.check_output(["python", os.path.join(THIS_DIR, "../bin/calc_slowdown.py"), tf.name, p_name], stderr = null)
        import re
        return float(re.sub(r'\\def\\.+\{(.+)\}', r'\1', val))

ss_slowdown = get_slowdown("subsonic")
jf_slowdown = get_slowdown("jforum")
of_slowdown = get_slowdown("openfire")

of_errors = subprocess.check_output(["python", os.path.join(THIS_DIR, "../bin/calc_error_stat.py"), "openfire"] + list(of_result))
ss_errors = subprocess.check_output(["python", os.path.join(THIS_DIR, "../bin/calc_error_stat.py"), "subsonic"] + list(ss_result))
jf_errors = subprocess.check_output(["python", os.path.join(THIS_DIR, "../bin/calc_error_stat.py"), "jforum"] + list(jf_result))

if len(sys.argv) < 2:
    print ss_slowdown
    print jf_slowdown
    print of_slowdown

    print of_errors
    print ss_errors
    print jf_errors
else:
    def mk_dict(slow, error):
        return {
            "slowdown": slow,
            "error": float(error.strip())
        }
    with open(sys.argv[1], 'w') as out:
        yaml.dump({
            "subsonic": mk_dict(ss_slowdown, ss_errors),
            "jforum": mk_dict(jf_slowdown, jf_errors),
            "openfire": mk_dict(of_slowdown, of_errors)
        }, out)
