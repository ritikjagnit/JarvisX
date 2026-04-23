import queue
import threading
import time

class CommandWorker:
    """
    CENTRAL COMMAND QUEUE SYSTEM
    Multithreaded architecture handling both voice and dashboard inputs.
    It guarantees requests are instantly stored, prioritized, and executed efficiently
    without freezing the input collectors.
    """
    def __init__(self, command_router_callback, response_callback=None):
        # Thread-safe PriorityQueue ensures high-priority items execute first
        self.cmd_queue = queue.PriorityQueue()
        self.command_router_callback = command_router_callback
        self.response_callback = response_callback
        self.is_running = True
        
        # Start Main Worker Thread
        threading.Thread(target=self._worker_loop, daemon=True, name="JarvisCentralWorker").start()
        print("[DEBUG] Command Worker Queue Thread Initialized.")

    def enqueue(self, command, source="dashboard", priority=2):
        if not command:
            return
            
        # Priority Queue Tuples structure: (priority, insert_time, item_data)
        # Using insert_time to ensure FIFO stability when priorities are equal.
        item = (priority, time.time(), command, source)
        self.cmd_queue.put(item)
        print(f"[QUEUE] Task added: '{command}' | Source: {source} | Priority: {priority}")

    def _execute_and_respond(self, command):
        """ Runs the command synchronously within this execution thread, then dispatches result. """
        response_text = self.command_router_callback(command)
        
        # 1. CENTRALIZE RESPONSE HANDLING
        if response_text and self.response_callback:
            print(f"[DEBUG] Central Response handler firing speech for: '{response_text}'")
            self.response_callback(response_text)

    def _worker_loop(self):
        while self.is_running:
            try:
                # Blocks efficiently until a task is available
                priority, timestamp, command, source = self.cmd_queue.get()
                print(f"[WORKER] Pulled task: '{command}' (Priority: {priority})")
                
                # Non-blocking executor pattern: 
                # Execute in an isolated thread to immediately free up the worker to grab the next queue item.
                threading.Thread(
                    target=self._execute_and_respond, 
                    args=(command,), 
                    daemon=True,
                    name=f"ExecutionThread-{timestamp}"
                ).start()
                
                self.cmd_queue.task_done()
            except Exception as e:
                print(f"[WORKER] Critical queue error: {e}")
                time.sleep(1)
