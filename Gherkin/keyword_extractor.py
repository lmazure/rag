import json
import re
import uuid
import argparse
import sys

from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

def condense_keyword(keyword: str, string_delimiter: str = '"') -> str:
    """
    Condense a keyword by removing any specific integer, float, strings, or parameter name.
    Args:
        keyword: The keyword to condense
        string_delimiter: The string delimiter to use (either " or ')
    """
    condensed_keyword = re.sub(r'<[^>]*>', '<>', keyword)
    condensed_keyword = re.sub(f'{string_delimiter}[^{string_delimiter}]*{string_delimiter}', f'{string_delimiter}{string_delimiter}', condensed_keyword)
    condensed_keyword = re.sub(r'\d+\.\d*', '12.34', condensed_keyword)
    condensed_keyword = re.sub(r'\d+', '123', condensed_keyword)
    return condensed_keyword

def extract_keywords_from_feature_file(file_path: str, string_delimiter: str = '"') -> list[dict[str, str]]:
    """
    Extract Gherkin keywords from a single feature file.
    Return a list of dictionaries containing keyword type, text, and description.
    """
    # Read the feature file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return []

    # Parse the feature file
    parser = Parser()
    try:
        feature = parser.parse(TokenScanner(content))
    except Exception as e:
        print(f"Error parsing file {file_path}: {str(e)}", file=sys.stderr)
        sys.exit(1)
    if 'feature' not in feature:
        print(f"Error parsing file {file_path}: Feature not found", file=sys.stderr)
        sys.exit(1)

    # Process each feature (it can either be a scenario or a background, but we do not care, we can retrieve the steps the same way)
    keywords = []
    for component in feature['feature']['children']:
        lastKeywordType = None
        component_data = next(iter(component.values()))
        assert isinstance(component_data, dict)
        assert 'steps' in component_data
        for step in component_data['steps']:
            step_type = step['keywordType']
            if (step_type == 'Conjunction'):
                if (lastKeywordType == None):
                    print("Conjunction without previous keyword", file=sys.stderr)
                    sys.exit(1)
                else:
                    step_type = lastKeywordType
            else:
                lastKeywordType = step_type
            keyword = step['text'].strip()
            condensed_keyword = condense_keyword(keyword, string_delimiter)
            keywords.append({
                'type': step_type,
                'keyword': keyword,
                'condensed_keyword': condensed_keyword,
                'description': '',
                'id': str(uuid.uuid4())
            })

    return keywords

def sort_keywords(keywords: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Sort keywords first by type (Context, Action, Outcome), then alphabetically by keyword text.
    """
    # Define the order of keyword types
    type_order = {'Context': 1, 'Action': 2, 'Outcome': 3}

    # Sort the keywords
    return sorted(
        keywords,
        key=lambda x: (
            type_order.get(x['type'], 999),  # First sort by type (using 999 for unknown types)
            x['keyword'].lower()             # Then sort alphabetically (case-insensitive)
        )
    )

def consolidate_keywords(new_keywords: list[dict[str, str]], all_keywords: list[dict[str, str]]) -> None:
    """
    Add the new keywords into the existing list of all keywords.
    If a keyword with the same type and condensed keyword already exists,
    the longest keyword is kept.
    """
    for kw in new_keywords:
        existing_keyword = next((k for k in all_keywords if ((k['type'] == kw['type']) and (k['condensed_keyword'] == kw['condensed_keyword']))), None)
        if existing_keyword:
            print(f"Duplicate keyword: old='{existing_keyword['keyword']}' new='{kw['keyword']}'")
            if len(existing_keyword['keyword']) > len(kw['keyword']):
                # we keep the already recorded keyword which is longer
                continue
            else:
                # the new keyword is longer, we remove the old one
                all_keywords.remove(existing_keyword)
        all_keywords.append(kw)

def process_feature_files(file_paths: list[str], string_delimiter: str = '"') -> dict:
    """
    Process multiple feature files and return a dictionary with unique, sorted keywords.
    """
    all_keywords = []
    
    for file_path in file_paths:
        if file_path.endswith('.feature'):
            keywords = extract_keywords_from_feature_file(file_path, string_delimiter)
            consolidate_keywords(keywords, all_keywords)
    
    # Sort the keywords
    sorted_keywords = sort_keywords(all_keywords)

    # Remove the `condensed_keyword` field
    for kw in sorted_keywords:
        del kw['condensed_keyword']

    return {'keywords': sorted_keywords}

def main():

    parser = argparse.ArgumentParser(description='Extract keywords from Gherkin feature files and save them to a JSON file.')
    parser.add_argument('feature_files', nargs='+', help='One or more .feature files to process')
    parser.add_argument('output_file', help='Output JSON file to store the extracted keywords')
    parser.add_argument('--string_delimiter', choices=['"', "'"], default='"', help='String delimiter to use when condensing keywords (default: ")')
    args = parser.parse_args()

    # Process the files and get the keywords
    result = process_feature_files(args.feature_files, args.string_delimiter)
    
    # Write the result to a JSON file
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
