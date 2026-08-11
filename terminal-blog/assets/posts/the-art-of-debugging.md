# The Art of Debugging

Debugging is not just finding bugs. It is understanding the system well enough to predict its failures.

## The mindset

- Reproduce first, fix later
- Read the logs before adding print statements
- Form a hypothesis, then test it

## Tools of the trade

| Tool | Purpose |
|------|---------|
| `gdb` | Low-level inspection |
| `strace` | System call tracing |
| `wireshark` | Network archaeology |
| `printf` | The original debugger |
