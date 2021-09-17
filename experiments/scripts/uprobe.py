from bcc import BPF
from bcc.utils import printb

ebpf_prog = """
#include <uapi/linux/ptrace.h>

int start(struct pt_regs* ctx)
{
  bpf_trace_printk("Intercepted user func add() at start\\n");
  return 0;
}

int end(struct pt_regs* ctx)
{
  bpf_trace_printk("Intercepted user func add() at end ret:%d\\n", PT_REGS_RC(ctx));
  return 0;
}
"""

user_exec_prog_path = "/root/ebpf/python/bin/test"
user_func_symbol1 = "main.add"

b = BPF(text=ebpf_prog)
b.attach_uprobe(name=user_exec_prog_path, sym=user_func_symbol1, fn_name="start")
b.attach_uretprobe(name=user_exec_prog_path, sym=user_func_symbol1, fn_name="end")

print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "MESSAGE"))
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        exit()
    printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
