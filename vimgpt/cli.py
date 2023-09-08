import argparse
import logging

from pynvim import NullHandler

from vimgpt.core import vimgpt_agent


def main():
    parser = argparse.ArgumentParser(description="VimGPT Entry Point")

    # Required arguments
    parser.add_argument("filepath", type=str, help="File for VimGPT to open.")
    parser.add_argument(
        "command",
        type=str,
        help="Task for VimGPT to perform on the file, in natural language: 'Rename Bob to Bill in paragraph 2`, make arg 'user' optional on line 34', 'rewrite this in iambic pentameter', etc.",
    )

    # Optional arguments
    parser.add_argument(
        "--socket",
        "-s",
        type=str,
        default=None,
        help="Path to nvim socket of running nvim process. If left empty, VimGPT will run in headless mode. Suggested value: '/tmp/nvimsocket'.",
    )
    parser.add_argument(
        "--loglevel",
        type=str.upper,  # Convert to uppercase for consistent handling
        choices=["DEBUG", "INFO", "WARNING"],
        default="WARNING",
        help="Set the logging level (default: %(default)s)",
    )
    # Add max_calls argument
    parser.add_argument(
        "--max-calls",
        type=int,
        default=1000,
        help="Maximum number of calls. Default is 1000.",
    )

    # Add delay_seconds argument
    parser.add_argument(
        "--delay-seconds",
        type=int,
        default=None,
        help="Delay in seconds. If not provided, defaults to None.",
    )

    args = parser.parse_args()

    # Remove the NullHandler from the root logger if it's there.
    # see: https://github.com/neovim/pynvim/issues/373
    for handler in logging.root.handlers:
        if isinstance(handler, NullHandler):
            logging.root.removeHandler(handler)

    # configuring logging here is fine because CLI is the entry point;
    # library consumers will import vimgpt.core instead
    logging.basicConfig(level=args.loglevel)
    logger = logging.getLogger(__name__)

    with open(args.filepath, "r") as file:
        content = file.read()

    logger.debug(f"VimGPT successfully read file: {args.filepath}")
    return vimgpt_agent(
        args.filepath,
        content,
        args.command,
        args.socket,
        args.max_calls,
        args.delay_seconds,
    )


if __name__ == "__main__":
    main()
