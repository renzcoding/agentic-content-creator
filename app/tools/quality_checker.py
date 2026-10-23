
import re

from config.settings import MIN_SCRIPT_LENGTH


def quality_check(script: str, topic: str = "") -> dict:
    """Evaluate the structure and content of a generated script."""
    issues = []
    normalized = script.lower()

    if topic:
        topic_words = {
            word.lower()
            for word in re.findall(r"\b\w+\b", topic)
            if len(word) > 3
        }
        
        ignored_topic_words = {
            "cara", "untuk", "dalam", "dengan", "yang",
            "agar", "bisa", "pada", "memanfaatkan",
        }
        topic_words -= ignored_topic_words

        if topic_words and not any(
            word in normalized for word in topic_words
        ):
            issues.append(
                "The script may not be relevant to the requested topic."
            )

    if len(script) < MIN_SCRIPT_LENGTH:
        issues.append("The script is too short.")

    if len(script.split()) > 100:
        issues.append("The script is too long for a short-form video.")

    if normalized.count("misalnya") >= 4:
        issues.append("The script overuses the same example transition.")

    if normalized.count("memastikan anda dapat lebih fokus") >= 2:
        issues.append("The script repeats the same productivity claim.")

    required_sections = ("HOOK:", "BODY:", "CTA:")

    for section in required_sections:
        if not any(
            line.strip().upper().startswith(section)
            for line in script.splitlines()
        ):
            issues.append(f"The {section[:-1].lower()} section is missing.")

    quote_pairs = {
        '"': '"',
        "'": "'",
        "“": "”",
        "‘": "’",
    }

    stripped_script = script.rstrip()

    if stripped_script:
        last_char = stripped_script[-1]

        if last_char in ('"', "'", "”", "’"):
            quote_count = sum(
                script.count(opening)
                for opening in quote_pairs
            )

            closing_count = sum(
                script.count(closing)
                for closing in quote_pairs.values()
            )

            if quote_count > closing_count:
                issues.append("The script may end with an incomplete quotation.")

    if script.rstrip().endswith(("...", "…")):
        issues.append("The script may be truncated.")

    cta_line = next(
        (
            line.strip()
            for line in script.splitlines()
            if line.strip().upper().startswith("CTA:")
        ),
        "",
    )

    if len(cta_line.split()) < 5:
        issues.append("The CTA is incomplete or too short.")    

    placeholders = (
        "[opening sentence]",
        "[three practical points",
        "[closing call to action]",
        "[practical point",
        "[example",
        "[insert",
        "[website",
        "[contact",
        "[your ",
        "fill in",
        "add your",
        "as an ai",
        "i cannot",
        "i am unable",
    )

    if any(phrase in normalized for phrase in placeholders):
        issues.append("The script contains placeholders or refusal text.")

    english_phrases = (
        "hey guys",
        "welcome to our channel",
        "today, we're going to",
        "first off",
        "let's dive right in",
        "happy exploring",
    )

    if any(phrase in normalized for phrase in english_phrases):
        issues.append("The script appears to contain English phrases.")

    for section in ("HOOK:", "BODY:", "CTA:"):
        if script.count(section) > 1:
            issues.append("The script contains repeated sections.")
            break

    if "waktudan" in normalized:
        issues.append("The script contains incorrectly joined words.")

    
    sentences = [
        re.sub(r"\s+", " ", sentence.strip().lower())
        for sentence in re.split(r"[.!?]+", script)
        if len(sentence.strip().split()) >= 6
    ]

    body_match = re.search(
        r"BODY:\s*(.*?)(?=\n\s*CTA:|$)",
        script,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if body_match:
        body_lines = [
            re.sub(r"^\s*\d+\.\s*", "", line).strip().lower()
            for line in body_match.group(1).splitlines()
            if re.match(r"^\s*\d+\.\s+", line)
        ]


        normalized_lines = [
            re.sub(r"[^\w\s]", "", line)
            for line in body_lines
        ]

        if len(normalized_lines) != len(set(normalized_lines)):
            issues.append("The body contains duplicated key points.")

        stop_words = {
            "yang", "dan", "di", "ke", "dari", "untuk",
            "dengan", "ini", "itu", "atau", "dalam",
            "anda", "adalah", "dapat", "bisa", "tidak",
            "ai", "membantu", "melakukan", "memastikan",
        }

        point_keywords = [
            {
                word for word in re.findall(r"\b\w+\b", line)
                if len(word) > 3 and word not in stop_words
            }
            for line in body_lines
        ]

        for first in range(len(point_keywords)):
            for second in range(first + 1, len(point_keywords)):
                common = point_keywords[first] & point_keywords[second]
                smaller_size = min(
                    len(point_keywords[first]),
                    len(point_keywords[second]),
                )

                if (
                    len(common) >= 3
                    and smaller_size > 0
                    and len(common) / smaller_size >= 0.7
                ):
                    issues.append(
                        f"Body points {first + 1} and {second + 1} may repeat the same idea."
                    )

        if len(body_lines) != 3:
            issues.append(
                "The body must contain exactly three numbered key points."
            )

        for index, line in enumerate(body_lines, start=1):
            if len(line.split()) < 5:
                issues.append(
                    f"Body point {index} is too short or lacks useful detail."
                )

    words = re.findall(r"\b[\w'-]+\b", normalized)
    ignored_words = {
        "yang", "dan", "di", "ke", "dari", "untuk",
        "dengan", "ini", "itu", "atau", "dalam", "kita",
        "anda", "adalah", "dapat", "bisa", "tidak", "the",
        "jika", "kamu", "membantu", "sering",
        "kerja", "ai", "tugas",
    }
    meaningful_words = [
        word for word in words
        if word not in ignored_words and len(word) > 3
    ]

    if meaningful_words:
        repeated_words = {
            word for word in set(meaningful_words)
            if meaningful_words.count(word) >= 6
            and word not in {"waktu", "ai", "kerja", "doa", "tidur"}
        }

        if repeated_words:
            issues.append(
                "The script overuses words: "
                + ", ".join(sorted(repeated_words))
            )

    if "muslim_faceless" in normalized or "doa" in normalized:
        religious_phrases = (
            "doa adalah kembang yang tumbuh dari hati",
            "doa untuk allah",
        )
        if any(phrase in normalized for phrase in religious_phrases):
            issues.append(
                "The script contains religious claims that need source verification."
            )


    if len(sentences) != len(set(sentences)):
        issues.append("The script contains duplicated sentences.")

    return {
        "approved": len(issues) == 0,
        "issues": issues,
    }
