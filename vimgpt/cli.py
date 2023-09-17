import argparse
import logging

from pynvim import NullHandler

from vimgpt.core import vimgpt_agent


def main():
    default_output_file = "vimgpt_output.txt"
    parser = _vimgpt_cli_parser(default_output_file)
    args = parser.parse_args()

    # Remove the NullHandler from the root logger if it's there.
    # see: https://github.com/neovim/pynvim/issues/373
    for handler in logging.root.handlers:
        if isinstance(handler, NullHandler):
            logging.root.removeHandler(handler)

    # configuring logging here is fine because CLI is the entry point;
    # library consumers will import vimgpt.core instead
    logging.basicConfig(level=args.loglevel, format="%(message)s")
    logger = logging.getLogger(__name__)

    content = ""
    if args.path is not None:
        with open(args.path, "r") as file:
            content = file.read()
    logger.debug(f"VimGPT successfully read file: {args.path}")

    rewritten = vimgpt_agent(
        command=args.command,
        original_content=content,
        file_path=args.path,
        socket=args.socket,
        max_calls=args.max_calls,
        delay_seconds=args.delay_seconds,
        model=args.model,
    )

    # Determine where to write the output
    if args.output is None:
        logger.info("VimGPT: No output file specified, not saving changes to disk.")
    else:
        # If args.output is empty string and args.path is specified, write to args.path
        # If args.output is empty string and args.path is not specified, write to default_output_file
        output_path = (
            args.path
            if args.output == "" and args.path
            else args.output or default_output_file
        )

        with open(output_path, "w") as file:
            file.write(rewritten)

        logger.info(f"VimGPT: Changes saved to: {output_path}")


def _vimgpt_cli_parser(default_output_file):
    parser = argparse.ArgumentParser(description="VimGPT CLI")

    # Required arguments
    parser.add_argument(
        "command",
        type=str,
        help="Task for VimGPT to perform on the file, in natural language: 'Rename Bob to Bill in paragraph 2`, 'make arg `user` optional on line 34', 'rewrite this in iambic pentameter', etc.",
    )

    # Optional arguments
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        default=None,
        help="File for VimGPT to open. NOTE: for safety, VimGPT will NOT make changes directly to the file unless the --output flag is provided.",
    )

    parser.add_argument(
        "--output",
        "-o",
        nargs="?",
        default=None,  # Placeholder to be checked later
        const="",
        help=f"Specify output file. If flag is not provided, VimGPT will NOT make changes directly to the file. If flag is provided without value, uses the same path as the input file. If flag is provided with no value and there is no input file specified, will output to '{default_output_file}'.",
    )

    parser.add_argument(
        "--socket",
        "-s",
        type=str,
        default=None,
        help="Path to nvim socket of running nvim process. If left empty, VimGPT will run in headless mode. Suggested value: '/tmp/nvimsocket'.",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="gpt-4",
        help="The specific model to be used. Default is 'gpt-4'",
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

    return parser


if __name__ == "__main__":
    main()
