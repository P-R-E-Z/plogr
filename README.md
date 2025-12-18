[![Lint Status](https://github.com/P-R-E-Z/plogr/actions/workflows/lint.yml/badge.svg)](https://github.com/P-R-E-Z/plogr/actions/workflows/lint.yml)

# plogr

**plogr** is a cross-distro/platform package-activity logger that records every install and removal event on your system, then writes an append-only history in both JSON and TOML. It can also monitor your downloads(configurable) folder for new files.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Package-manager integration](#package-manager-integration)

<details>
<summary><strong>4. Configuration</strong></summary>

&nbsp;&nbsp;1. [User Scope](#user-scope-default)<br/>
&nbsp;&nbsp;2. [System Scope](#system-scope-requires-administrator)<br/>
&nbsp;&nbsp;3. [DNF Plugin Configuration](#dnf-plugin-configuration)

</details>

<details>
<summary><strong>5. Usage</strong></summary>

&nbsp;&nbsp;1. [Setup](#setup)<br/>
&nbsp;&nbsp;2. [Check Status](#check-status)<br/>
&nbsp;&nbsp;3. [Start Monitoring](#start-monitoring)<br/>
&nbsp;&nbsp;4. [Query Logs](#query-logs)<br/>
&nbsp;&nbsp;5. [Export Logs](#export-logs)<br/>
&nbsp;&nbsp;6. [Manual Logging](#manual-logging)

</details>

6. [Shell Integration](#shell-integration)
7. [Log File Examples](#log-file-examples)
8. [TODO List](TODO.md)
9. [Contributing](CONTRIBUTING.md)

## Features

- **Zero-maintenance Hooks** - hooks directly into DNF4 and DNF5; no polling required.
- **Native DNF5 Plugin** - C++ plugin for DNF5 with automatic transaction logging.
- **Dual Log Formats** - automatically mirrors entries to `packages.json` and `packages.toml` files.
- **Modular Backends** - easily extendable with backends for APT, Pacman, Homebrew, etc.
- **Append-Only History** - entries are never deleted; removals are flagged as removed.
- **Scope-Aware Logging** - choose between user-only (`--scope user`) or system-wide (`--scope system`) package tracking.
- **Download Monitoring** - automatically log files downloaded to your Downloads folder.
- **Log Querying** - search and filter your package history directly from the CLI.

---

## Installation

Package builds will soon be available from my Copr repository.  Until then:

* **Fedora / RHEL** – build & install the RPM as shown below (automatic DNF integration).
* **All other platforms** – install the pure-Python package with `pipx` (or `pip`) and, if you like, add a small hook so your package manager calls the CLI automatically.

### Quick install via pipx (works everywhere)

```bash
# system Python → isolated environment in ~/.local/pipx:
pipx install plogr==0.7.0

# verify
plogr --help
```

Supported Python versions: 3.12–3.13 (3.14 is blocked until upstream PyO3/pydantic-core add support). If your system default is newer, set `UV_PYTHON=python3.13` when building or installing with `uv`/`pipx`.

You can now enable the download-monitoring service:

```bash
systemctl --user daemon-reload   # first time only
systemctl --user enable --now plogr.service
```

### DNF5 Plugin Installation

The RPM package includes a native C++ plugin for DNF5 that provides automatic package logging via the DNF5 Actions Plugin system.

#### Automatic Installation (RPM)

When you install the RPM package, the DNF5 plugin is automatically:

1. **Built** using CMake with libdnf5 dependencies
2. **Installed** to `/usr/lib64/dnf5/plugins/plogr.so`
3. **Configured** with Actions Plugin hooks at `/usr/share/libdnf5/plugins/actions.d/plogr.actions`
4. **Enabled** by default for automatic transaction logging

#### Manual Installation

If you're building from source or need to install manually:

```bash
# Install build dependencies
sudo dnf install cmake gcc-c++ libdnf5-devel pkgconfig

# Build and install the plugin
cd libdnf5-plugin/dnf5-plugin
mkdir build && cd build
cmake ..
make
sudo make install
```

#### Plugin Verification

Verify the plugin is working:

```bash
# Check DNF5 version
dnf5 --version

# Test plugin loading (should show no errors)
dnf5 list installed | head -5

# Check if transactions are being logged
plogr status
```

### (Optional) DIY hooks for other package managers

<details>
<summary><strong>APT / Debian & Ubuntu</strong></summary>

1. Create `/etc/apt/apt.conf.d/99plogr` (system-wide) or `~/.config/apt/apt.conf.d/99plogr` (user):

```conf
DPkg::Post-Invoke { "plogr install-apt-hook || true"; };
```

2. Put a tiny helper on your PATH, e.g. `/usr/local/bin/plogr-install-apt-hook`:

```bash
#!/usr/bin/env bash
# Log every package touched in the most recent dpkg transaction
awk '{print $4}' /var/log/dpkg.log | tail -n +2 | while read -r pkg; do
  plogr install "$pkg" apt
done
```

Make it executable (`chmod +x …`).

</details>

<details>
<summary><strong>Pacman / Arch</strong></summary>

Create `/etc/pacman.d/hooks/plogr.hook`:

```ini
[Trigger]
Operation = Install
Operation = Upgrade
Operation = Remove
Type      = Package
Target    = *

[Action]
Description = Log package transaction with plogr
When        = PostTransaction
Exec        = /usr/bin/plogr pacman-hook %t
```

`%t` is the transaction database path; you can parse it inside `pacman-hook` to emit individual `plogr install/remove` calls.

</details>

<details>
<summary><strong>Other managers</strong></summary>

For Homebrew, Chocolatey and Winget, use manual logging or adapt the examples above. Read _Package-manager integration_ and [CONTRIBUTING](CONTRIBUTING.md) for what’s still needed.

</details>

---

## Package-manager integration

<details>
<summary><strong>Linux</strong></summary>

| Package manager | Status | Setup |
|-----------------|--------|-------|
| **DNF4** (Fedora/RHEL) | Automatic logging via Python plugin | See [DNF Plugin Configuration](#dnf-plugin-configuration). The RPM installs `/usr/lib/python3.*/site-packages/dnf-plugins/plogr.py` and a sample config; enable it with `enabled=1`. |
| **DNF5** (Fedora/RHEL) | Automatic logging via native C++ plugin | See [DNF Plugin Configuration](#dnf-plugin-configuration). The RPM installs `/usr/lib64/dnf5/plugins/plogr.so` and is enabled by default. |
| **APT** (Debian/Ubuntu) | Planned | Parser exists (`apt.py`), but no hook yet. A `DPkg::Post-Invoke` script is needed. Help welcome → [Contributing](CONTRIBUTING.md) |
| **Pacman** (Arch) | Planned | Parser exists (`pacman.py`). Needs an `alpm` hook (`/etc/pacman.d/hooks/plogr.hook`). See [Contributing](CONTRIBUTING.md) |

</details>

<details>
<summary><strong>macOS</strong></summary>

| Package manager | Status | Notes |
|-----------------|--------|-------|
| **Homebrew** | Planned | Parsing implemented (`brew.py`). Requires a post-install wrapper or Homebrew *tap* to invoke the CLI automatically. See [Contributing](CONTRIBUTING.md). |

</details>

<details>
<summary><strong>Windows</strong></summary>

| Package manager | Status | Notes |
|-----------------|--------|-------|
| **Chocolatey** | Planned | Parser implemented (`chocolatey.py`). Needs a PowerShell extension/post-install script. |
| **Winget** | Planned | Parser implemented (`winget.py`). Requires a `winget` source extension or scheduled task to call the CLI. |

See the [Contributing guide](CONTRIBUTING.md) if you’d like to help wire up these back-ends.

</details>

---

## Configuration

### User Scope (Default)

User scope logs packages for the current user only. Files are stored in `~/.local/share/plogr/`.

**Configuration file**: `~/.config/plogr/plogr.conf`

```json
{
  "scope": "user",
  "enable_dnf_hooks": true,
  "enable_download_monitoring": true,
  "downloads_dir": "~/Downloads",
  "monitored_extensions": ".rpm, .deb, .pkg, .exe, .msi, .dmg",
  "log_format": "both"
}
```

### System Scope (Requires Administrator)

System scope logs packages system-wide. Files are stored in `/var/log/plogr/`.

**Configuration file**: `/etc/plogr/plogr.conf`

```json
{
  "scope": "system",
  "enable_dnf_hooks": true,
  "enable_download_monitoring": false,
  "log_format": "both"
}
```

### DNF Plugin Configuration

plogr includes both a Python plugin for DNF4 and a native C++ plugin for DNF5.

#### DNF4 (Python Plugin)

**User scope**: `~/.config/dnf/plugins/plogr.conf`

```ini
[main]
enabled = 1
scope = user
```

**System scope**: `/etc/dnf/plugins/plogr.conf`

```ini
[main]
enabled = 1
scope = system
```

#### DNF5 (Native C++ Plugin)

The DNF5 plugin is automatically installed to `/usr/lib64/dnf5/plugins/plogr.so` and is enabled by default.

**User scope**: `~/.config/dnf5/plugins/plogr.conf`

```ini
[main]
enabled = 1
scope = user
```

**System scope**: `/etc/dnf5/plugins/plogr.conf`

```ini
[main]
enabled = 1
scope = system
```

#### Troubleshooting DNF5 vs DNF4

- **DNF5 plugin not loading**: Ensure you're using DNF5 (`dnf5 --version`) and the plugin is installed to `/usr/lib64/dnf5/plugins/`
- **DNF4 plugin not loading**: Ensure you're using DNF4 (`dnf --version`) and the plugin is installed to `/usr/lib/python3.*/site-packages/dnf-plugins/`
- **Both plugins installed**: The system will use the appropriate plugin based on which DNF version you're running
- **Plugin conflicts**: Only one plugin should be active at a time; the Python plugin is for DNF4, the C++ plugin is for DNF5
- **DNF5 transactions not logged**: Check that the Actions Plugin file at `/usr/share/libdnf5/plugins/actions.d/plogr.actions` exists and has no trailing characters
- **Scope detection issues**: Run `sudo plogr setup` to properly configure system scope, or use `plogr setup` for user scope
- **Configuration conflicts**: Ensure only one config file exists - either system (`/etc/plogr/`) or user (`~/.config/plogr/`)

---

## Usage

All commands can be run with `--scope user` (default) or `--scope system` (requires `sudo`).

### Setup

Initializes configuration and directories.
```bash
plogr setup
```

### Check Status

Show current status and statistics.
```bash
plogr status
```

### Start Monitoring

Starts the monitoring daemon. For users, this monitors the downloads directory.
```bash
# Start download monitoring (user scope only, foreground)
plogr daemon

# Run in background (non-systemd, POSIX only)
plogr daemon --background

# Run continuously via systemd-user service
# (the unit file is shipped in /usr/lib/systemd/user by the RPM)
#
# 1. Reload user units to ensure systemd sees the new file
systemctl --user daemon-reload
# 2. Enable + start the logger – this will automatically create
#    ~/.config/systemd/user/ if it does not already exist.
systemctl --user enable --now plogr.service

# Note: The systemd service includes security hardening that restricts
# access to only the log directory and Downloads folder. If you use a
# custom downloads directory, you may need to modify the service file.

# Optional: keep the service running even after logging out
sudo loginctl enable-linger "$USER"
```
> System scope requires sudo. Without it, commands fall back to user scope and emit a warning.

### Query Logs

Search the package logs.
```bash
# Find all packages with 'nginx' in the name
plogr query --name nginx

# Find packages installed with dnf in the last 30 days
plogr query --manager dnf --days 30
```

### Export Logs

Export the full log to stdout.
```bash
# Export user logs as JSON
plogr export --format json
```

### Manual Logging

Manually log a package installation or removal.
```bash
# Log a package installation
plogr install package-name dnf

# Log a package removal
plogr remove package-name dnf

# Log a downloaded file
plogr install downloaded-file.zip download
```

---

## Shell Integration

### Shell wrapper to log every git clone

#### .zshrc

```bash
function pkglog_preexec() {
    [[ $1 == git\ clone* ]] || return
    local repo=${${1#git clone }##*/}
    repo=${repo%.git}
    plogr install $repo git
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec pkglog_preexec
```

#### .bashrc

```bash
function _pkglog_bash_preexec() {
   [[ $BASH_COMMAND == git\ clone* ]]  || return
   local repo=${BASH_COMMAND#git clone}
   repo=${repo##*/}
   repo=${repo%.git}
   plogr install "$repo" git
}
```

#### config.fish

```bash
function fish_preexec --on-event fish_preexec
  if string match -rq '^git clone ' -- $argv[1]
    set repo (basename (string replace -r '^git clone +' '' $argv[1]) .git)
    plogr install $repo git
  end
end
```

---

## Log File Examples

### JSON Format

```json
[
  {
    "name": "neovim",
    "manager": "dnf",
    "action": "install",
    "date": "2025-06-21T17:02:41-05:00",
    "removed": false,
    "scope": "user",
    "version": "0.9.5-1.fc42",
    "metadata": {
      "arch": "x86_64",
      "repo": "fedora"
    }
  },
  {
    "name": "firefox-120.0.tar.bz2",
    "manager": "download",
    "action": "install",
    "date": "2025-06-21T18:30:15-05:00",
    "removed": false,
    "scope": "user",
    "metadata": {
      "file_path": "/home/user/Downloads/firefox-120.0.tar.bz2",
      "file_size": 52428800,
      "file_type": ".tar.bz2"
    }
  }
]
```

### TOML Format

```toml
[[package]]
name = "neovim"
manager = "dnf"
action = "install"
date = "2025-06-21T17:02:41-05:00"
removed = false
scope = "user"
version = "0.9.5-1.fc42"

[package.metadata]
arch = "x86_64"
repo = "fedora"

[[package]]
name = "firefox-120.0.tar.bz2"
manager = "download"
action = "install"
date = "2025-06-21T18:30:15-05:00"
removed = false
scope = "user"

[package.metadata]
file_path = "/home/user/Downloads/firefox-120.0.tar.bz2"
file_size = 52428800
file_type = ".tar.bz2"
```

---

## File Locations

### User Scope

- **Log files**: `~/.local/share/plogr/`
  - `packages.json`
  - `packages.toml`
- **Configuration**: `~/.config/plogr/plogr.conf`
- **DNF plugin config**: `~/.config/dnf/plugins/plogr.conf`

### System Scope

- **Log files**: `/var/log/plogr/`
  - `packages.json`
  - `packages.toml`
- **Configuration**: `/etc/plogr/plogr.conf`
- **DNF plugin config**: `/etc/dnf/plugins/plogr.conf`

---

## Building the RPM yourself

With the provided `Makefile`, building and installing a local version of the RPM is simple.

```bash
# Create the SRPM and RPM packages
make rpm

# Install the newly built package
make install

# Supported Python: 3.12–3.13. Python 3.14 is currently blocked because PyO3/pydantic-core
# do not yet support it. If your system Python is newer, set build envs to 3.13:
# UV_PYTHON=python3.13 PYO3_PYTHON=python3.13 make rpm
# UV_PYTHON=python3.13 PYO3_PYTHON=python3.13 make install
```

The `Makefile` handles placing the source tarball in the correct `rpmbuild` directory for you.

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

---

## License

MIT License (see LICENSE)

---

## **Use of AI on this project**

I currently use AI to help me with scaffolding, research, debugging, and documentation. All other aspects of the code is done by me, keep in mind I do this for fun so keep your expectations low... lol.
