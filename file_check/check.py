import re
import traceback
import json
from pathlib import Path
from typing import List
from packaging.specifiers import SpecifierSet, InvalidSpecifier, Specifier
from packaging.version import parse


class IncorrectVersion(Exception):
    """Raised when incorrect version is found"""


class FileCheck:

    def __init__(self, file_list: str, header_lines: str, base_ver: str, line_regex: str) -> None:
        self.file_list = file_list
        self.header_lines = header_lines
        self.base_ver = base_ver
        self.line_regex = line_regex
        self.issue_no = 1
        self.summary = []

    @staticmethod
    def _remove_comments(content: str) -> List:
        """Remove comments from content"""
        patterns = [
            '(""".*?""")',
            "('''.*?''')",
            "(#.*?\n)",
        ]
        comment_pattern = "|".join(patterns)
        content = re.sub(comment_pattern, "\n", content, flags=re.DOTALL)
        sanitized = content.split("\n")
        sanitized = [line.strip() for line in sanitized if line.strip()]
        return sanitized

    def _log_error(self, line: str, trace: str) -> bool:
        """Log error for specific line"""
        message = f"{self.issue_no}. Line:\n\t{line}\ntriggered following issue during check:\n"
        msg = f"\n{message}\n{trace}\n"
        self.summary.append(msg)
        self.issue_no += 1
        return False

    def _check_header_line(self, line: str) -> bool:
        """Check header line"""
        _, str_list = line.split("=")
        try:
            eval(str_list)
            return True
        except SyntaxError:
            return self._log_error(line, traceback.format_exc())

    def _check_specifier_set(self, specifier_set: SpecifierSet) -> None:
        """Check specifier set"""
        msg = []
        for specifier in specifier_set:
            if parse(specifier.version).major != int(self.base_ver):
                msg.append(f"Incorrect version: {specifier.version}, only version {self.base_ver}.x is allowed")
        if msg:
            raise IncorrectVersion("\n".join(msg))

    def _check_def_line(self, line: str) -> bool:
        """Check line based on given regex, also check version specifiers"""
        try:
            groups = re.search(self.line_regex, line)
            _, _, tags, ver = groups.groups()
            eval(tags.strip())
            if ver:
                self._check_specifier_set(SpecifierSet(ver))
            return True
        except InvalidSpecifier as e:
            return self._log_error(
                line,
                "Invalid version specifier format: "
                f"{e}\nAccepted specifiers (from packaging module):{json.dumps(Specifier._operators, indent=4)}"
            )
        except SyntaxError:
            return self._log_error(line, traceback.format_exc())
        except IncorrectVersion as e:
            return self._log_error(line, e)
        except Exception:
            return self._log_error(line, f"Error in line syntax, used search pattern: {self.line_regex}")

    def _check_line(self, line: str):
        """Check line"""
        for header_line in self.header_lines:
            if line.startswith(header_line):
                return self._check_header_line(line)
        return self._check_def_line(line)

    def _check_file(self, file: str) -> bool:
        """Check file line by line"""
        content = Path(file).read_text()
        content = self._remove_comments(content)
        self.summary.append(f"--> Checking file {file}...")
        return all([self._check_line(line) for line in content])

    def check(self) -> bool:
        """Check all files"""
        return all([self._check_file(file) for file in self.file_list])
