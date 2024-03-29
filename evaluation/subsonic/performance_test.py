import subprocess
import os.path
import time
import sys
import eval_tools

THIS_DIR = os.path.realpath(os.path.dirname(sys.argv[0]))
test_output = open(os.path.join(THIS_DIR, 'test.log'), 'w')
measure_mem = False
eval_tools.log_file = test_output
eval_tools.kill_memlistener()
STACCATO_DIR = os.path.join(THIS_DIR, '../../')

#TIMEOUT=1000

def do_test(mode, test_name, iterations = None):
    subprocess.call(["sudo", os.path.join(THIS_DIR, "../tomcat_control"), "stop"], stdout = test_output, stderr = subprocess.STDOUT)
    subprocess.call(["sudo", os.path.join(THIS_DIR, "../deploy_wrapper"), "subsonic", mode], stdout = test_output, stderr = subprocess.STDOUT)
    test_file = os.path.join(THIS_DIR, "ss_test2.jmx")
    eval_tools.warmup_jmeter(test_file)
    rspec = eval_tools.RunSpec(measure_mem, STACCATO_DIR, THIS_DIR)
    return eval_tools.run_jmeter(rspec, test_file, test_name, 60839, iterations)


iterations = 100

if len(sys.argv) > 1 and sys.argv[1] == "--full":
    iterations = 350
    del sys.argv[1]

mode = "inst"

if len(sys.argv) > 1 and sys.argv[1] == "mem":
    mode = "mem"
    measure_mem = True

ret1 = do_test(mode, "inst", iterations)
ret2 = do_test("base", "base", iterations)

subprocess.call(["sudo", os.path.join(THIS_DIR, "../tomcat_control"), "stop"], stdout = test_output, stderr = subprocess.STDOUT)

print ret1, ret2
