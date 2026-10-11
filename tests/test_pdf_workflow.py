from app.main import find_today_date_matches


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
