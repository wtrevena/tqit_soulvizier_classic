"""Cheap CI check for the patches-registry manifest (no DB build required).

Validates that every module named in tools/patches/__init__.py REGISTRY imports
cleanly and satisfies the module contract (MODULE_NAME str + apply callable),
and that the manifest has no duplicate entries. Prints the manifest order hash.

Run from the repo root:
    py tools/patches/_check_registry.py

Exit code 0 = OK; non-zero (SystemExit) = a contract violation to fix before the
build. This is the fast pre-flight; the byte-identical empty-registry build
(tools/patches/README.md S5) is the full identity proof.
"""
import os
import sys

# Put tools/ on sys.path so `import patches` resolves this package, exactly as
# build_svc_database.py sees it.
_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import patches  # noqa: E402

if __name__ == '__main__':
    sys.exit(patches.selfcheck())
