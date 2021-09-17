from bcc import BPF
from bcc.utils import printb

ebpf_prog = """
#include <uapi/linux/ptrace.h>

int start(struct pt_regs* ctx)
{
  bpf_trace_printk("Intercepted sys call clone() at start\\n");
  return 0;
}

int end(struct pt_regs* ctx)
{
  bpf_trace_printk("Intercepted sys call clone() at end ret:%d\\n", PT_REGS_RC(ctx));
  return 0;
}
"""

sys_call_name = "__x64_sys_clone"

b = BPF(text=ebpf_prog)
#b.attach_kprobe(event=b.get_syscall_fnname("clone"), fn_name="hello")
b.attach_kprobe(event=sys_call_name, fn_name="start")
b.attach_kretprobe(event=sys_call_name, fn_name="end")

print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "MESSAGE"))
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        exit()
    printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
