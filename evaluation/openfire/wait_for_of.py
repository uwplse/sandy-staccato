import os.path

def wait_for_openfire(of_proc, log_file):
    _wait_for_logfile(of_proc, log_file)
    with open(log_file, "r") as f:
        _wait_for_server(f)

def _wait_for_logfile(of_proc, log_file):
    import time
    while True:
        if of_proc.poll() is not None:
            print "Openfire failed to start"
            import sys
            sys.exit(-1)
        if not os.path.exists(log_file):
            time.sleep(0.5)
        else:
            break

def _wait_for_server(f):
    assert f is not None
    while True:
        new = f.readline()
        if new and new.startswith("Admin console listening at"):
            break
        elif not new:
            import time
            time.sleep(0.5)
