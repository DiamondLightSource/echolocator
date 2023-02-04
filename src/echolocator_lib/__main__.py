import json
from argparse import ArgumentParser

from echolocator_lib.version import meta, version


def get_parser():
    parser = ArgumentParser(
        description="XChem GUI for manually targeting drop points for the Echo dispenser."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version(),
        help="Print version string.",
    )
    parser.add_argument(
        "--version-json",
        action="store_true",
        help="Print version stack in json.",
    )
    return parser


def main(args=None):
    parser = get_parser()
    args = parser.parse_args(args)

    if args.version_json:
        print(json.dumps(meta(), indent=4))


if __name__ == "__main__":
    main()
