import logging
import re
import time
from pathlib import Path

import httpcore
from googletrans import Translator
from googletrans.models import Translated

DEFAULT_FOLDER = "locales"
DEFAULT_SRC_LANG = "en"
PATTERN = re.compile(
    r"#:(.*?)\nmsgid\s(.*?)msgstr\s(.*?)\n\n", re.MULTILINE | re.DOTALL
)

fmt = "[%(asctime)s] %(message)s (%(levelname)s) [%(name)s]"
date_fmt = "%d.%m.%y %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=date_fmt)
for logger_name in ("hpack", "httpx"):
    logging.getLogger(logger_name).setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def qouted(text: str, sq='"', eq='"') -> str:
    return f"{sq}{text}{eq}"


def unqouted(text: str, sq='"', eq='"') -> str:
    return text.removeprefix(sq).removesuffix(eq)


def parse_text(text: str):
    lines = text.strip().split("\n")
    lines = (unqouted(line.strip()) for line in lines)
    lines = (line.replace(r"\n", "\n") for line in lines)
    return "".join(lines)


def build_text(text: str):
    lines = text.strip().replace("\n", "\\n\n").split("\n")
    lines = (qouted(line) for line in lines)
    return "\n".join(lines)


def work_with_file(target_lang, po_file: Path, translator):
    result: list[str] = []
    logger.debug(f"{target_lang} {po_file}")
    text = po_file.read_text(encoding="utf-8")
    last = 0
    for m in PATTERN.finditer(text):
        place = m.group(1).strip()
        msgid = parse_text(m.group(2))
        msgstr = parse_text(m.group(3))
        start, end = m.start(3), m.end(3)
        logger.info(place)

        if not msgstr.strip():
            r = None
            try:
                tr: Translated = translator.translate(
                    msgid, dest=target_lang, src=DEFAULT_SRC_LANG
                )

                r = build_text(tr.text)
                logger.debug(f"{msgid} -> {r}")
                time.sleep(0.2)
            except httpcore._exceptions.ReadTimeout as e:
                logger.error(e)
                time.sleep(1)

            if r is not None:
                result.append(text[last:start])
                result.append(r)
                last = end
            else:
                result.append(text[last:end])

    result.append(text[last:])
    result_text = "".join(result)
    po_file.write_text(result_text, encoding="utf-8")


def main():
    translator = Translator()

    folder = Path("locales")
    for po_file in folder.rglob("*.po"):
        target_lang = po_file.parent.parent.name
        work_with_file(target_lang, po_file, translator)


if __name__ == "__main__":
    main()
