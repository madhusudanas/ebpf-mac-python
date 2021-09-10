#!/usr/bin/env python3

from bcc import BPF
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import threading

clone_ebpf = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/fs.h>

#define ARGSIZE  128

BPF_PERF_OUTPUT(events);

struct data_t {
    u32 pid;  // PID as in the userspace term (i.e. task->tgid in kernel)
    u32 ppid; // Parent PID as in the userspace term (i.e task->real_parent->tgid in kernel)
    u32 uid;
    char comm[TASK_COMM_LEN];
};

int clone_ebpf(struct pt_regs *ctx) {
    struct data_t data = {};
    struct task_struct *task;

    data.uid = bpf_get_current_uid_gid() & 0xffffffff;
    data.pid = bpf_get_current_pid_tgid() >> 32;
    
    task = (struct task_struct *)bpf_get_current_task();
    data.ppid = task->real_parent->tgid;

    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    events.perf_submit(ctx, data, sizeof(struct data_t));

    return 0;
}
"""

pid = ""
ppid = ""
uid = ""
command = ""

def clone_ebpf_thread():
    b = BPF(text=clone_ebpf)
    clone_fn_name = b.get_syscall_fnname("clone")
    b.attach_kprobe(event=clone_fn_name, fn_name="clone_ebpf")
    b["events"].open_perf_buffer(collect_events)
    while 1:
      try:
          b.perf_buffer_poll()
      except KeyboardInterrupt:
          exit()


def collect_events():
    event = b["events"].event(data)
    pid = event.pid
    ppid = event.ppid
    uid = event.uid
    command = event.comm

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("received a get message", sys.stdout)
        self.send_response(200)
        self.end_headers()
        response = "pid: " + pid + " ppid: " + ppid + " uid: " + uid + " command: " + command
        self.wfile.write(response)

x = threading.Thread(target=clone_ebpf_thread)
x.start()
httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
