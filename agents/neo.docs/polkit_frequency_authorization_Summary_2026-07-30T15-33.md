# Scoped Polkit Frequency Authorization Summary

## Outcome

Implemented the deferred custom Polkit action for Perf-Dock. The action uses
`auth_admin_keep`, so authentication is retained briefly for repeated frequency
changes without weakening generic `pkexec` authorization.

## Changes

- Added `scripts/perf-dock-helper`, a root-installed helper accepting only
  `governor NAME` and `range MIN|- MAX|-` operations.
- Added `packaging/io.github.perf-dock.policy`, scoped to the exact installed
  helper path `/usr/libexec/perf-dock-helper`.
- Updated the controller to prefer the installed helper and retain the legacy
  direct-pkexec fallback when it is absent.
- Added `make install-polkit` and documented installation/behavior.
- Added controller, helper validation, injection-rejection, and policy tests.

## Verification

- `make test`: PASS, 63 tests.
- `make lint`: PASS, pylint 10.00/10; Ruff, format, Radon, Vulture, Bandit clean.
- `git diff --check`: PASS.

## Installation Status

System installation was attempted but cancelled because the execution channel
cannot accept the user's sudo password. Neither system file was installed. The
user must run `make install-polkit` in their own interactive terminal once.
