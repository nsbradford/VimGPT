import argparse
import logging

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
        "--verbose", "-v", action="store_true", help="Sets logging level to debug."
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

    # logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)
    logger = logging.getLogger(__name__)

    with open(args.filepath, "r") as file:
        content = file.read()

    logger.debug(f"VimGPT opened file: {args.filepath}")
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
