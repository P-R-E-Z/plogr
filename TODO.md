# TODO List

## Priorities
1. **Medium**: Complete remaining C++ plugin testing (build system, install paths)
2. **Low**: Improve CLI scope-mismatch messaging (verify UX across commands)
3. **Low**: Improve CMake configuration error handling

## Open Items

<details>
<summary>CLI and Configuration Improvements</summary>

- [ ] **Improve CLI defaults**  
  - [ ] Add better error messages when scope mismatch occurs  
  - [ ] Consider adding `--auto-detect-scope` option
- [x] **Add background flag to daemon**  
  - [x] Add `--background` flag to `plogr daemon` command  
  - [x] Implement background forking logic  
  - [x] Add proper signal handling for background mode
- [ ] **Config file precedence** *(complete)* — prefer system config when present  
</details>

<details>
<summary>Testing and Quality Assurance</summary>

- [ ] **Add unit tests for C++ plugin**  
  - [ ] Test build system with different compilers  
  - [ ] Test installation paths and permissions  
</details>

<details>
<summary>Package Manager Backends</summary>

- [ ] **Implement APT backend hooks**  
  - [ ] Create `DPkg::Post-Invoke` script  
  - [ ] Add APT configuration examples  
  - [ ] Test with Debian/Ubuntu systems
- [ ] **Implement Pacman backend hooks**  
  - [ ] Create `/etc/pacman.d/hooks/plogr.hook`  
  - [ ] Implement transaction parsing  
  - [ ] Test with Arch Linux systems
- [ ] **Implement Homebrew backend hooks**  
  - [ ] Create post-install wrapper or tap  
  - [ ] Test with macOS systems
- [ ] **Implement Windows backends**  
  - [ ] Chocolatey PowerShell extension  
  - [ ] Winget source extension or scheduled task
</details>

<details>
<summary>Monitoring and Logging</summary>

- [ ] **Enhance download monitoring**  
  - [ ] Add file type detection improvements  
  - [ ] Add virus scanning integration  
  - [ ] Add duplicate file detection  
  - [ ] Add file metadata extraction
- [ ] **Improve log querying**  
  - [ ] Add more search filters  
  - [ ] Add date range queries  
  - [ ] Add export format options  
  - [ ] Add log rotation support
</details>

<details>
<summary>Performance and Reliability</summary>

- [ ] **Optimize log file handling**  
  - [ ] Add log file compression  
  - [ ] Add log file rotation  
  - [ ] Add backup and recovery features  
  - [ ] Add log file integrity checks
- [ ] **Add error recovery**  
  - [ ] Handle plugin loading failures gracefully  
  - [ ] Add retry mechanisms for failed operations  
  - [ ] Add fallback logging mechanisms
</details>

<details>
<summary>Future Enhancements</summary>

- [ ] **Add web interface**  
  - [ ] Simple web dashboard for viewing logs  
  - [ ] REST API for log access  
  - [ ] Real-time log streaming
- [ ] **Add notification system**  
  - [ ] Email notifications for package changes  
  - [ ] Desktop notifications  
  - [ ] Slack/Discord integration
- [ ] **Add analytics and reporting**  
  - [ ] Package usage statistics  
  - [ ] System change reports  
  - [ ] Dependency analysis
- [ ] **Improve Windows support**  
  - [ ] Native Windows service  
  - [ ] Windows-specific package managers  
  - [ ] Windows registry monitoring
- [ ] **Improve macOS support**  
  - [ ] Native macOS service  
  - [ ] macOS-specific package managers  
  - [ ] macOS security considerations
- [ ] **Add Git integration**  
  - [ ] Log git clone operations  
  - [ ] Track repository changes  
  - [ ] Version control integration
- [ ] **Add container support**  
  - [ ] Docker container monitoring  
  - [ ] Podman container monitoring  
  - [ ] Container image tracking
</details>

## Completed Items

<details>
<summary>CLI and Configuration Improvements</summary>

- [x] **Add background flag to daemon**  
  - [x] Add `--background` flag to `plogr daemon` command  
  - [x] Implement background forking logic  
  - [x] Add proper signal handling for background mode
- [x] **Improve CLI defaults** - CLI respects configured scope by default  
- [x] **Config file precedence** - Prefer system config when present to match README and avoid scope surprises  
</details>

<details>
<summary>Build System Improvements</summary>

- [x] **Add development dependencies to RPM spec**  
  - [x] Include `libdnf5-devel` and `libdnf5-cli-devel`  
  - [x] Add `cmake` and `pkg-config` as build dependencies  
  - [x] Consider adding `gcc-c++` explicitly
</details>

<details>
<summary>Monitoring and Logging</summary>

- [x] **Logger consistency cleanup** - Remove or document unused `_append_toml` helper  
- [x] **TOML availability warning** - Emit one-time warning when `toml` package is absent  
</details>

<details>
<summary>Testing and Quality Assurance</summary>

- [x] **Add integration tests for DNF5 plugin**  
  - [x] Test plugin loading in DNF5 environment  
  - [x] Test transaction logging functionality  
  - [x] Test plugin configuration options  
  - [x] Test error handling scenarios
- [x] **Add unit tests for C++ plugin**  
  - [x] Test plugin interface implementation
</details>

<details>
<summary>Documentation and Installation</summary>

- [x] **Fix man page installation**  
  - [x] Add man page to RPM spec file (`docs/man/plogr.1` → `%{_mandir}/man1/`)  
  - [x] Ensure man page is properly formatted and installed  
  - [x] Test man page accessibility
- [x] **Add post-install messages**  
  - [x] Add post-install script to RPM spec  
  - [x] Display configuration instructions  
  - [x] Show how to enable DNF plugin  
  - [x] Provide systemd service setup instructions
</details>

<details>
<summary>Code Quality and Docs</summary>

- [x] **Clean up backend code**  
  - [x] Cleaned dnf.py, apt.py, pacman.py, brew.py, chocolatey.py, winget.py  
  - [x] Moved detailed setup instructions to CONTRIBUTING.md  
  - [x] Maintained focus on DNF backend while providing basic layouts for other backends
- [x] **Enhanced CONTRIBUTING.md**  
  - [x] Added dropdown menus and collapsible sections  
  - [x] Added comprehensive backend setup instructions  
  - [x] Added pre-submission checklist for contributors  
  - [x] Enhanced troubleshooting section with Git/release-specific issues  
  - [x] Added development workflow documentation
- [x] **Fixed critical Makefile issue**  
  - [x] Fixed `make release` to properly commit changes before pushing  
  - [x] Added proper git workflow with staging, commit, and push  
  - [x] Updated documentation to reflect corrected workflow
- [x] **Enhanced GitHub Actions workflow**  
  - [x] Fixed release.yml with proper dependencies and permissions  
  - [x] Enhanced security with step-level environment variables  
  - [x] Improved error handling and directory management  
  - [x] Fixed context access warnings in shell scripts
</details>

<details>
<summary>Comprehensive Test Suite Overhaul</summary>

- [x] Created integration tests for DNF backend (`tests/integration/test_dnf_backend.py`)  
- [x] Enhanced unit tests with proper mocking and fixtures  
- [x] Added new test files for hooks and monitors  
- [x] Fixed test isolation issues with module reloading  
- [x] Resolved import and mocking issues for missing dnf module
</details>

<details>
<summary>Backend Code Improvements</summary>

- [x] Fixed DNF backend with proper TYPE_CHECKING imports  
- [x] Added conditional imports and error handling for missing modules  
- [x] Enhanced plugin imports with proper error handling  
- [x] Improved type hints and error messages throughout codebase
</details>

<details>
<summary>Updated Documentation</summary>

- [x] Update README.md with DNF5 plugin information  
- [x] Add troubleshooting section for DNF5 vs DNF4  
- [x] Document plugin configuration for both DNF versions  
- [x] Update installation instructions
</details>

<details>
<summary>DNF5 Plugin Implementation</summary>

- [x] Fixed DNF plugin installation path  
- [x] Implemented native libdnf5 C++ plugin (CMake build)  
- [x] Fixed CMake build configuration (C++20, pkg-config deps)  
- [x] Fixed plugin interface implementation (all required virtuals)  
- [x] Fixed RPM build system (CMake macros, build dir)  
- [x] Fixed installation paths (`/usr/lib64/dnf5/plugins/`)  
- [x] Fixed TypeError in plugin code (naming conflict)  
- [x] System-level systemd service installed via RPM spec  
  - [x] Security hardening (ProtectSystem, ProtectHome, PrivateTmp, NoNewPrivileges)  
  - [x] Proper network dependency handling  
  - [x] Fixed Documentation field to use URL
</details>

## Notes

- Focus on CLI improvements and documentation first.  
- Ensure changes work with both DNF4 and DNF5.  
- Maintain backward compatibility.  
- Monitor impact on package manager performance.