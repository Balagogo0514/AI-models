---
name: c-code-review
description: Use when reviewing C code changes, especially embedded, systems, drivers, firmware, runtime, or security-sensitive code, and the review should prioritize correctness, memory and resource safety, undefined behavior, concurrency or ISR hazards, hardware-facing failure modes, security impact, and missing tests.
---

# C Code Review

## Overview

Review for production risk, not aesthetics. Prefer concrete behavioral failures, broken invariants, realistic race windows, memory hazards, security consequences, and missing tests over style comments.

## Output Format

Always report in this order:

1. Findings
2. Open questions or assumptions
3. Brief summary

Put findings first and order them by severity. Cite file and line references when available. If no meaningful findings exist, say so directly and note residual risk or missing coverage.

## Review Standard

Ignore:

- formatting preferences
- naming nits unless they hide a bug
- subjective style disagreements
- refactors unrelated to correctness, safety, or maintainability

Focus on:

- correctness and state invariants
- memory, ownership, lifetime, and cleanup
- undefined behavior, integer, pointer, aliasing, and alignment risks
- concurrency, ISR, atomicity, volatile misuse, and teardown races
- hardware-facing issues such as register ordering, reserved bits, timing, reset, DMA, and timeout handling
- security surfaces, trust boundaries, attacker-controlled sizes or offsets, and unsafe parsing
- missing tests for failure paths, boundaries, concurrency, malformed input, and regressions

## Review Flow

Review in this order:

1. Understand the intended behavior and touched interfaces.
2. Check happy path and failure path correctness.
3. Check memory, ownership, cleanup, and partial initialization.
4. Check low-level C hazards and undefined behavior.
5. Check concurrency, ISR, and hardware interaction risks.
6. Check security impact and trust-boundary handling.
7. Check whether tests prove the risky paths.

## Findings Bar

Report a finding when there is a concrete failure mode, broken invariant, realistic race window, memory or UB hazard, security consequence, or a missing test that hides a high-risk path.

If something is suspicious but not provable from the available diff or files, move it to open questions instead of guessing.

## No-Finding Case

If no meaningful issues are found, state that explicitly. Still mention residual risk, unverified assumptions, or missing coverage if they matter.
