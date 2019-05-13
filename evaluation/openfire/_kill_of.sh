function kill_of {
	kill -9 $(ps aux | grep startup.jar | grep -v grep | awk '{print $2}') 2>/dev/null || true
}
