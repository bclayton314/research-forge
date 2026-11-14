from app.search import (
    make_snippet,
    parse_query,
    score_text,
)


def test_parse_query():
    terms = parse_query(
        "Boxer Rebellion in China"
    )

    assert terms == [
        "boxer",
        "rebellion",
        "in",
        "china",
    ]


def test_score_text():
    text = (
        "China experienced unrest. "
        "The Boxer movement developed "
        "in northern China."
    )

    score = score_text(
        text,
        [
            "china",
            "boxer",
        ],
    )

    assert score == 3


def test_make_snippet_returns_short_text():
    text = "Short research passage."

    snippet = make_snippet(
        text,
        ["research"],
    )

    assert snippet == text


def test_make_snippet_limits_long_text():
    text = (
        ("A" * 400)
        + " Boxer "
        + ("B" * 400)
    )

    snippet = make_snippet(
        text,
        ["boxer"],
        max_length=300,
    )

    assert "Boxer" in snippet

    assert len(snippet) <= 306