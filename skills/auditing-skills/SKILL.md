---
name: auditing-skills
description: Use when downloading, importing, or reviewing skills and scripts from external sources to verify safety before execution.
---

# Auditing Skills

## Overview

This skill mandates a strict security review process for any downloaded code or skills. It prevents the execution of malicious logic, credential theft, and system destruction by enforcing a three-stage audit: Basic Check, Deep Review, and Sandbox Testing.

## When to Use

* **Before** using any skill downloaded from the internet.
* **Before** running any external script (`.sh`, `.py`, `.js`).
* **When** asked to review code for security vulnerabilities.

## 1. Basic Checks

**Stop and check these explicitly.** Do not skim.

### A. Dangerous Keywords

Search for these terms in all files (`SKILL.md`, scripts, code):

* `curl`, `wget` (Network requests)
* `bash`, `sh`, `exec`, `system`, `subprocess` (Shell execution)
* `eval` (Dynamic code execution - **CRITICAL**)
* `pickle`, `ctypes` (Python unsafe ops)
* `child_process`, `vm` (Node.js unsafe ops)
* `silently`, `background`, `hidden` (Stealth behavior)
* `base64`, `atob` (Obfuscation)

### B. Sensitive Paths

Check for access to:

* `~/.ssh` (Keys)
* `~/.aws` (Cloud credentials)
* `~/.config` (App configs)
* `/var/run/docker.sock` (Docker daemon access - **ROOT ACCESS**)
* `.env`, `credentials` (Secrets)
* `/etc/passwd`, `/etc/shadow` (System users)

### C. Network & Dependencies

* **HTTP/HTTPS:** Where is data going? Unknown domains?
* **Installations:** Does it use `-g` or `--global`? Is the version fixed?

## 2. Deep Review

If the skill contains scripts (`.js`, `.py`, `.sh`), you **MUST**:

1. **Read every line.** Do not assume functionality based on function names.
2. **De-obfuscate.** Decode any Base64 or hex strings immediately.
    * Example: `eval(atob("..."))` -> **DANGER**
3. **Check persistence.** Look for cron jobs, background services, or startup file modifications (`.bashrc`, `.zshrc`).
4. **Static Analysis.** Use tools if possible:
    * Python: `bandit -r .`
    * JS: `eslint --plugin security .`

## 3. Sandbox Testing (Recommended)

**NEVER** run untrusted code on your main environment. Use a disposable sandbox.

If the skill contains executable code, **prompt the user to confirm they are using a sandbox environment** before execution.

Ask the user: "Have you verified these scripts in an isolated sandbox environment?"

## Red Flags - STOP and REJECT

If you see these, **DO NOT RUN** the skill. Report it immediately.

* `rm -rf` or file deletion commands.
* Sending credentials (`~/.ssh`, `~/.aws`) to a URL.
* `curl | bash` without inspection.
* Encoded/Obfuscated logic (`eval`, `base64`).
* Pre-compiled binaries or opaque executables.

## Common Rationalizations (Do NOT Fall for These)

| Excuse | Reality |
|--------|---------|
| "It's just a simple script." | Simple scripts can wipe disks in 1 line. |
| "I'll read it quickly." | Obfuscation (`base64`) hides malware from quick reads. |
| "It's from a repository." | Repositories can be compromised (typosquatting). |
| "I'll run it and see." | Once run, the damage is done (exfiltration). |

## Verification

After auditing, confirm:

1. [ ] No dangerous keywords found (or justified).
2. [ ] No sensitive paths accessed.
3. [ ] Code de-obfuscated and understood.
4. [ ] Tested in sandbox (if executable).
