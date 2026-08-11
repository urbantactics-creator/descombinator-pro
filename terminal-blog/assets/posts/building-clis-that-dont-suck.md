# Building CLIs That Don't Suck

Most CLIs are built for machines, not humans. Let's fix that.

## Principles

1. **Predictable output** — machines parse it, humans read it
2. **Progressive disclosure** — simple by default, powerful when needed
3. **Composability** — pipes and redirects are features, not hacks

## The forgotten art of help text

```
$ mytool --help
USAGE
  mytool [OPTIONS] <input>

OPTIONS
  -o, --output FILE    Write result to FILE
  -v, --verbose        Enable debug logging
  -h, --help           Show this message
```
