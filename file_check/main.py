import argparse
from file_check.check import FileCheck


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--header_lines", nargs="+", required=True, help="Starting strings for specific lines (headers)")
    parser.add_argument("--base_ver", type=str, required=True, help="Major version number to be used")
    parser.add_argument("--line_regex", type=str, required=True, help="Regex expression for checking lines")
    parser.add_argument("--doc_string", default="", type=str, help="Help which will be displayed after errors reporting")
    args = parser.parse_args()

    checker = FileCheck(args.filenames, args.header_lines, args.base_ver, args.line_regex)
    result = checker.check()

    if not result:
        print(f"\nIdentified {checker.issue_no - 1} issue(s):\n")
        print("\n".join(checker.summary))
        print(f"\n{args.doc_string}")
        return 1

    return 0


if __name__ == "__main__":
    main()
