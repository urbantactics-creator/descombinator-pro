"""tests/shim_aifc.py – early monkey‑patch for the removed stdlib aifc module.

The module must be imported once before any test that pulls in audioread.
It replaces the missing ``aifc`` name in ``sys.modules`` with a minimal stub
so the DeprecationWarning about ``aifc was removed in Python 3.13`` never fires.
"""

import sys
import types

# Remove any stale aifc that might already be present
if "aifc" in sys.modules:
    del sys.modules["aifc"]

# Build a lightweight stub that mimics the attributes used by audioread.
_stub = types.ModuleType("aifc")
_stub.open = open  # passthrough to built‑in open
_stub.COMPRESS_CMP = 0x01  # constants audioread expects
_stub.COMPRESS_MAX_SIZE_k = 512 * 1024
_stub.COMPRESS_LEVEL = 6
# Install the stub into sys.modules
sys.modules["aifc"] = _stub
