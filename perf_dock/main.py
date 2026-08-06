"""Main Entry Point for the Perf-Dock Tray Application."""

import argparse
import logging
import signal
import sys

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import GLib, Gtk

    HAS_GRAPHICS = True
except (ImportError, ValueError) as e:
    HAS_GRAPHICS = False
    GRAPHICS_ERROR = e

from perf_dock.controller import PerfDockController
from perf_dock.monitor import PerfDockMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("perf_dock.main")


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Perf-Dock: A tray controller for cpupower frequency scaling.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.5,
        help="Background monitor polling interval in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debugging logs",
    )
    parser.add_argument(
        "--gapplication-service",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main() -> int:
    """Main execution block."""
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    if args.gapplication_service:
        from perf_dock.service import run_service

        return run_service(poll_interval=args.poll_interval)

    if not HAS_GRAPHICS:
        logger.error(
            "System UI Libraries (Gtk 3.0 or AyatanaAppIndicator3 0.1) "
            "are not available.\n"
            "Ensure you have installed system dependencies "
            "(e.g., gir1.2-ayatanaappindicator3-0.1) "
            "and that you are running in a graphical X11/Wayland "
            "desktop environment.\n"
            "Error: %s",
            GRAPHICS_ERROR,
        )
        return 1

    logger.info("Initializing Perf-Dock tray application...")

    try:
        controller = PerfDockController()
        if not controller.is_available():
            logger.warning(
                "cpupower was not found on PATH. Perf-Dock will start in the "
                "error state until it is installed (see the tray menu for "
                "distro-specific install instructions)."
            )
        monitor = PerfDockMonitor(
            controller=controller, poll_interval=args.poll_interval
        )

        # Import UI indicator here to ensure it's loaded after GTK verification
        from perf_dock.ui_indicator import PerfDockIndicator

        indicator = PerfDockIndicator(controller=controller, monitor=monitor)

        monitor.start()

        def signal_handler(signum: int, _frame) -> None:
            logger.info(
                "Termination signal %d received. Initiating teardown...",
                signum,
            )
            indicator.shutdown()
            Gtk.main_quit()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        def sigint_timeout() -> bool:
            return True

        GLib.timeout_add(250, sigint_timeout)

        logger.info("Perf-Dock is successfully loaded. Running GTK Main Loop.")
        Gtk.main()

    except Exception as e:
        logger.exception(
            "An unhandled exception occurred during application lifetime: %s",
            e,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
