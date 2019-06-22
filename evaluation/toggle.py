import subprocess
import time
import sys
import os.path
import signal
import random

this_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

iterations = 100

class OpenfireControl(object):
    def __init__(self, of_bash):
        sys.path.append(os.path.join(this_dir, "openfire"))
        self.of_bash = of_bash
        
    def kill(self):
        of_pid = subprocess.check_output("ps aux | grep startup.jar | grep -v grep | awk '{print $2}'", shell=True).strip()
        os.kill(int(of_pid), signal.SIGKILL)

    def start(self):
        import tempfile
        log_temp = tempfile.NamedTemporaryFile(delete = True)
        of_proc = subprocess.Popen(["bash", self.of_bash], stdout = log_temp, stderr = subprocess.STDOUT)
        import wait_for_of
        wait_for_of.wait_for_openfire(of_proc, log_temp.name)

class TomcatControl(object):
    def __init__(self):
        pass

    def kill(self):
        subprocess.check_call(["sudo", os.path.join(this_dir, "tomcat_control"), "shutdown"])

    def start(self):
        subprocess.check_call(["sudo", os.path.join(this_dir, "tomcat_control"), "start"])

control_module = TomcatControl if sys.argv[1] == "tomcat" else OpenfireControl
iterations = int(sys.argv[2])
control = control_module(*sys.argv[3:])

sleep_rand = random.Random()
sleep_rand.seed((sys.argv[1], iterations))

# funny math
time.sleep(10)
        
for i in range(0, iterations):
    time.sleep(30)
    control.kill()
    control.start()
