import argparse
import logging

import vimgpt


def main():
    parser = argparse.ArgumentParser(description="VimGPT Entry Point")

    # Required arguments
    parser.add_argument("filepath", type=str, help="File for VimGPT to open.")
    parser.add_argument(
        "command", type=str, help="Task for VimGPT to perform on the file."
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

    args = parser.parse_args()

    # Set up logging
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)
    logger = logging.getLogger(__name__)

    # Your application logic here
    # logger.info(f"Opening file: {args.filepath}")
    # logger.info(f"Executing command: {args.command}")
    # if args.socket:
    #     logger.info(f"Using nvim socket: {args.socket}")
    # else:
    #     logger.info("Running in headless mode")

    with open(args.filepath, "r") as file:
        contents = file.read()

    logger.debug(f"VimGPT opened file: {args.filename}")
    return vimgpt(args.filename, contents, args.command, args.socket)


if __name__ == "__main__":
    main()
