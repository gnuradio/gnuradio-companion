# Copyright 2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import argparse
import logging
import os
import subprocess

try:
    from gnuradio import gr
except ImportError as ex:

    class Dummy:
        def version(self):
            return "0.0.0"

        def major_version(self):
            return "0"

        def api_version(self):
            return "0"

        def minor_version(self):
            return "0"

        def prefs(self):
            return {}

        def prefix(self):
            return "."

    gr = Dummy()

from .core import Messages
from .core.platform import Platform

from .utilities import logger as custom_logging

logger = logging.getLogger(__name__)


def argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Compile a GRC file (.grc) into a GNU Radio Python program and run it."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        default=".",
        help="Output directory for compiled program [default=%(default)s]",
    )
    parser.add_argument(
        "-u",
        "--user-lib-dir",
        action="store_true",
        default=False,
        help="Output to default hier_block library (overwrites -o)",
    )
    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        default=False,
        help="Run the program after compiling [default=%(default)s]",
    )
    parser.add_argument(
        metavar="GRC_FILE", dest="grc_files", nargs="+", help=".grc file to compile"
    )
    return parser


def main(args=None):
    # TODO: Only for testing!
    custom_logging.configure_logger(logging.TRACE)
    logger.notice("<<< Welcome to the GNU Radio Companion compiler (%s) >>>", gr.version())

    args = args or argument_parser().parse_args()

    platform = Platform(
        name="GNU Radio Companion Compiler",
        prefs=gr.prefs(),
        version=gr.version(),
        version_parts=(gr.major_version(), gr.api_version(), gr.minor_version()),
    )
    platform.build_library()

    output_dir = (
        args.output if not args.user_lib_dir else platform.config.hier_block_lib_dir
    )
    try:
        # recursive mkdir: os.makedirs doesn't work with .. paths, resolve with realpath
        os.makedirs(os.path.realpath(output_dir), exist_ok=True)
    except Exception as e:
        exit(str(e))

    flow_graph = file_path = None
    for grc_file in args.grc_files:
        os.path.exists(grc_file) or exit("Error: missing " + grc_file)
        Messages.send("\n")
        platform.config.hier_block_lib_dir = output_dir
        flow_graph, file_path = platform.load_and_generate_flow_graph(
            os.path.abspath(grc_file), os.path.abspath(output_dir)
        )
        if not file_path:
            exit("Compilation error")
    if file_path and args.run:
        run_command_args = flow_graph.get_run_command(file_path, split=True)
        subprocess.call(run_command_args)
