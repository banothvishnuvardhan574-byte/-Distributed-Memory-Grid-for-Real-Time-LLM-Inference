from app.main import find_today_date_matches, normalize_pdf_text


def test_find_today_date_matches_detects_today_entries():
    text = (
        "Project review on 11/oct at 10:00 AM.\n"
        "Next follow-up is on 12/oct.\n"
        "Reminder: 11/Oct status update due today."
    )

    matches = find_today_date_matches(text)

    assert len(matches) == 2
    assert all("11/" in match.lower() for match in matches)
    assert "11/oct" in matches[0].lower()


def test_find_today_date_matches_common_month_name_and_numeric_formats():
    text = (
        "Review on 11 October 2026.\n"
        "Follow-up on October 11th.\n"
        "Invoice dated 11-10-2026.\n"
        "US-style report dated 10/11/2026.\n"
        "The previous review was on 11 September."
    )

    matches = find_today_date_matches(text)

    assert len(matches) == 4
    assert matches == text.splitlines()[:4]


def test_find_today_date_matches_handles_empty_text():
    assert find_today_date_matches("") == []


def test_normalize_pdf_text_collapses_extraction_whitespace():
    assert normalize_pdf_text("  11   October\n2026  ") == "11 October 2026"
