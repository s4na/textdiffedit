"""Pin the local Formula to a merged commit and its downloaded source archive."""

import hashlib
import re
import sys
from pathlib import Path


def main():
    source_sha, version, archive = sys.argv[1:]
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise SystemExit("Expected a full commit SHA")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("Expected a numeric three-part version")

    formula = Path("Formula/textdiffedit.rb")
    text = formula.read_text(encoding="utf-8")
    marker = '  head "https://github.com/s4na/textdiffedit.git", branch: "main"'
    if text.count(marker) != 1:
        raise SystemExit("Unexpected Formula: missing or duplicate head declaration")
    checksum = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    stable = (
        f'  url "https://github.com/s4na/textdiffedit/archive/{source_sha}.tar.gz"\n'
        f'  version "{version}"\n'
        f'  sha256 "{checksum}"\n'
    )
    text = re.sub(r'^  (?:url|version|sha256) .*\n', '', text, flags=re.MULTILINE)
    formula.write_text(text.replace(marker, stable + marker), encoding="utf-8")


if __name__ == "__main__":
    main()
