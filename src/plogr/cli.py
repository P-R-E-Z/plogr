import click
import os
from functools import wraps
import datetime as dt
import json
import sys


def get_default_scope() -> str:
    """Return default scope; tests and CLI expect 'user' when not configured."""
    return "user"


def get_default_setup_scope() -> str:
    """Default to system when run as root for setup; otherwise user."""
    try:
        return "system" if os.geteuid() == 0 else "user"
    except Exception:
        return "user"


def require_sudo_for_system_scope(f):
    @wraps(f)
    def decorated_function(scope, *args, **kwargs):
        """Wrapper that ensures proper privilege for system scope."""
        if scope == "system" and os.geteuid() != 0:
            click.echo("Error: System scope requires administrative privileges.")
            click.echo("Falling back to user scope. Run with: sudo plogr <command> --scope system")
            scope = "user"

        return f(*args, scope=scope, **kwargs)

    return decorated_function


def _daemonize() -> bool:
    """Double-fork to background the process (POSIX only)."""
    if os.name == "nt":
        return False

    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)

        os.setsid()
        pid = os.fork()
        if pid > 0:
            os._exit(0)

        os.chdir("/")
        os.umask(0)

        with open(os.devnull, "rb", buffering=0) as read_null:
            os.dup2(read_null.fileno(), sys.stdin.fileno())
        with open(os.devnull, "ab", buffering=0) as write_null:
            os.dup2(write_null.fileno(), sys.stdout.fileno())
            os.dup2(write_null.fileno(), sys.stderr.fileno())
        return True
    except OSError as exc:
        click.echo(f"Failed to background daemon: {exc}")
        return False


@click.group()
def cli():
    """Plogr a local package installation and removal logger"""
    pass


@cli.command()
@click.option(
    "--setup",
    "scope",
    type=click.Choice(["user", "system"]),
    help="Setup configuration and directories",
    required=False,
)
@click.option("--system", "scope", flag_value="system", help="Setup configuration for system scope")
@click.option("--user", "scope", flag_value="user", help="Setup configuration for user scope")
@require_sudo_for_system_scope
def setup(scope):
    """Setup configuration and directories"""
    from .config import Config
    from .logger import PackageLogger

    if scope is None:
        scope = get_default_setup_scope()

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    click.echo(f"Setup complete for {scope} scope.")
    click.echo(f"Log directory created at: {logger.data_dir}")
    click.echo(f"Configuration saved to: {config.config_file}")


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def status(scope):
    """Show current status and statistics"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)
    stats = logger.get_statistics()

    click.echo(f"Scope: {stats['scope']}")
    click.echo(f"Total packages logged: {stats['total']}")
    click.echo(f"Installed: {stats['installed']}")
    click.echo(f"Removed: {stats['removed']}")
    click.echo(f"Downloads: {stats['downloads']}")
    click.echo(f"Log location: {logger.data_dir}")


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@click.option(
    "--background",
    is_flag=True,
    help="Run daemon in background (POSIX only; uses double-fork).",
)
@require_sudo_for_system_scope
def daemon(scope, background):
    """Start monitoring daemon"""
    import time
    from .config import Config
    from .logger import PackageLogger
    from .monitors.downloads import DownloadsMonitor

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    if background:
        if os.name == "nt":
            click.echo("Background mode is not supported on Windows.")
            return
        click.echo("Backgrounding daemon...")
        if not _daemonize():
            return

    if scope == "user":
        monitor = DownloadsMonitor(logger)
        try:
            monitor.start()
            if background:
                click.echo(f"Monitoring started in background (scope: {scope}).")
            else:
                click.echo(f"Monitoring started (scope: {scope}). Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
            click.echo("Monitoring stopped.")
    else:
        click.echo(f"System scope monitoring started (scope: {scope}).")
        click.echo("Download monitoring is only available in user scope.")
        if not background:
            click.echo("Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("Monitoring stopped.")


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@click.option("--format", default="json", type=click.Choice(["json", "toml"]))
@require_sudo_for_system_scope
def export(scope, format):
    """Export package log in specified format"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    if format == "json":
        click.echo(logger.json_file.read_text())
    else:
        click.echo(logger.toml_file.read_text())


@cli.command()
@click.argument("name")
@click.argument("manager")
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def install(name, manager, scope):
    """Log a package installation"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()
    logger = PackageLogger(config)
    logger.log_package(name, manager, "install")
    click.echo(f"Logged install of '{name}' using '{manager}'.")


@cli.command()
@click.argument("name")
@click.argument("manager")
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def remove(name, manager, scope):
    """Log a package removal"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()
    logger = PackageLogger(config)
    logger.log_package(name, manager, "remove")
    click.echo(f"Logged removal of '{name}' using '{manager}'.")


@cli.command()
@click.option("--name", default=None, help="Filter by package name (contains)")
@click.option("--manager", default=None, help="Filter by package manager")
@click.option("--days", default=None, type=int, help="Filter by days since log entry")
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def query(name, manager, days, scope):
    """Query the package log"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    since = None
    if days:
        since = dt.date.today() - dt.timedelta(days=days)

    results = logger.query(name=name, manager=manager, since=since)

    if not results:
        click.echo("No results found.")
        return

    for res in results:
        res_str = json.dumps(res, indent=2)
        click.echo(res_str)
