from ..keyword_extractor import consolidate_keywords, condense_keyword


def consolidate(new_keywords: list[dict[str, str]], all_keywords: list[dict[str, str]]) -> None:
    """
    Call the tested consolidate_keywords function
    """
    consolidate_keywords(add_condensed_keywords(new_keywords), add_condensed_keywords(all_keywords))


def add_condensed_keywords(keywords: list[dict[str, str]]) -> list[dict[str, str]]:
    """Add the condensed keywords in a keyword list"""
    for kw in keywords:
        kw['condensed_keyword'] = condense_keyword(kw['keyword'])
    return keywords


def test_consolidate_keywords_no_duplicates():
    """Test consolidation when there are no duplicate keywords"""
    # Arrange
    new_keywords = [
        {'type': 'Outcome', 'keyword': 'One'},
        {'type': 'Outcome', 'keyword': 'Two'}
    ]
    all_keywords = [
        {'type': 'then', 'keyword': 'Three'}
    ]
    
    # Act
    consolidate(new_keywords, all_keywords)
    
    # Assert
    assert len(all_keywords) == 3


def test_consolidate_keywords_embeding_string_with_duplicate_keep_longer():
    """Test that longer keyword is kept when duplicates are found"""
    # Arrange
    new_keywords = [
        {'type': 'Outcome', 'keyword': 'One "str"'},
        {'type': 'Outcome', 'keyword': 'Two'}
    ]
    all_keywords = [
        {'type': 'Outcome', 'keyword': 'One "my_str"'},
        {'type': 'Outcome', 'keyword': 'Three'}
    ]
    
    # Act
    consolidate(new_keywords, all_keywords)

    # Assert
    assert len(all_keywords) == 3
    assert any(kw['keyword'] == 'One "my_str"' for kw in all_keywords)
    assert any(kw['keyword'] == 'Two' for kw in all_keywords)
    assert any(kw['keyword'] == 'Three' for kw in all_keywords)


def test_consolidate_keywords_embeding_parameter_with_duplicate_keep_longer():
    """Test that longer keyword is kept when duplicates are found - case of parameter"""
    # Arrange
    new_keywords = [
        {'type': 'Outcome', 'keyword': 'One <param>'},
        {'type': 'Outcome', 'keyword': 'Two'}
    ]
    all_keywords = [
        {'type': 'Outcome', 'keyword': 'One <my_param>'},
        {'type': 'Outcome', 'keyword': 'Three'}
    ]
    
    # Act
    consolidate(new_keywords, all_keywords)

    # Assert
    assert len(all_keywords) == 3
    assert any(kw['keyword'] == 'One <my_param>' for kw in all_keywords)
    assert any(kw['keyword'] == 'Two' for kw in all_keywords)
    assert any(kw['keyword'] == 'Three' for kw in all_keywords)


def test_consolidate_keywords_embeding_float_with_duplicate_keep_longer():
    """Test that longer keyword is kept when duplicates are found - case of float"""
    # Arrange
    new_keywords = [
        {'type': 'Outcome', 'keyword': 'One 12.34€'},
        {'type': 'Outcome', 'keyword': 'Two'}
    ]
    all_keywords = [
        {'type': 'Outcome', 'keyword': 'One 1.2€'},
        {'type': 'Outcome', 'keyword': 'Three'}
    ]
    
    # Act
    consolidate(new_keywords, all_keywords)

    # Assert
    assert len(all_keywords) == 3
    assert any(kw['keyword'] == 'One 12.34€' for kw in all_keywords)
    assert any(kw['keyword'] == 'Two' for kw in all_keywords)
    assert any(kw['keyword'] == 'Three' for kw in all_keywords)


def test_consolidate_keywords_embeding_integer_with_duplicate_keep_longer():
    """Test that longer keyword is kept when duplicates are found - case of integer"""
    # Arrange
    new_keywords = [
        {'type': 'Outcome', 'keyword': 'One 12'},
        {'type': 'Outcome', 'keyword': 'Two'}
    ]
    all_keywords = [
        {'type': 'Outcome', 'keyword': 'One 1'},
        {'type': 'Outcome', 'keyword': 'Three'}
    ]
    
    # Act
    consolidate(new_keywords, all_keywords)

    # Assert
    assert len(all_keywords) == 3
    assert any(kw['keyword'] == 'One 12' for kw in all_keywords)
    assert any(kw['keyword'] == 'Two' for kw in all_keywords)
    assert any(kw['keyword'] == 'Three' for kw in all_keywords)


def test_consolidate_keywords_embeding_string_parameter_float_integer_with_duplicate_keep_longer():
    """Test that longer keyword is kept when duplicates are found - case of parameter, float, and integer"""
    # Arrange
    new_keywords = [
        {'type': 'Outcome', 'keyword': 'My "red" object has 2 items of type <wood> and costs $12785.'},
        {'type': 'Outcome', 'keyword': 'Two'}
    ]
    all_keywords = [
        {'type': 'Outcome', 'keyword': 'My "green" object has 7 items of type <water> and costs $96.1'},
        {'type': 'Outcome', 'keyword': 'Three'}
    ]
    
    # Act
    consolidate(new_keywords, all_keywords)

    # Assert
    assert len(all_keywords) == 3
    assert any(kw['keyword'] == 'My "green" object has 7 items of type <water> and costs $96.1' for kw in all_keywords)
    assert any(kw['keyword'] == 'Two' for kw in all_keywords)
    assert any(kw['keyword'] == 'Three' for kw in all_keywords)
