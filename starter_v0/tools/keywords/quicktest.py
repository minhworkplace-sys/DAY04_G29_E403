from tools.keywords.tool import extract_keywords


def main() -> None:
    result = extract_keywords("AI research improves AI safety and research", max_keywords=3)
    assert result["keywords"] == ["ai", "research", "improves"], result
    assert result["count"] == 3, result
    print("keywords quicktest: PASS")


if __name__ == "__main__":
    main()
