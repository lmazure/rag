import json
import re
import sys
import uuid

from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

def condense_keyword(keyword: str) -> str:
    """
    Condense a keyword by removing any specific integer, float, strings, or parameter name.
    """
    condensed_keyword = re.sub(r'<[^>]*>', '<>', keyword)
    condensed_keyword = re.sub(r'"[^"]*"', '""', condensed_keyword)
    condensed_keyword = re.sub(r'\d+\.\d*', '12.34', condensed_keyword)
    condensed_keyword = re.sub(r'\d+', '123', condensed_keyword)
    return condensed_keyword

def extract_keywords(file_path: str) -> list[dict[str, str]]:
    """
    Extract Gherkin keywords from a single feature file.
    Returns a list of dictionaries containing keyword type, text, and description.
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
    feature = parser.parse(TokenScanner(content))
    
    # Process each feature (it can either be a scenario or a background, but we does care, we can retrieve the steps the same way)
    keywords = []
    for component in feature['feature']['children']:
        lastKeywordType = None
        for step in next(iter(component.values()))["steps"]:
            step_type = step['keywordType']
            if (step_type == 'Conjunction'):
                if (lastKeywordType == None):
                    print("Conjunction without previous keyword")
                    sys.exit(1)
                else:
                    step_type = lastKeywordType
            else:
                lastKeywordType = step_type
            keyword = step['text'].strip()
            condensed_keyword = condense_keyword(keyword)
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

def process_feature_files(file_paths: list[str]) -> dict:
    """
    Process multiple feature files and return a dictionary with unique, sorted keywords.
    """
    all_keywords = []
    
    for file_path in file_paths:
        if file_path.endswith('.feature'):
            keywords = extract_keywords(file_path)
            for kw in keywords:
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
    
    # Sort the keywords
    sorted_keywords = sort_keywords(all_keywords)

    # Remove the `condensed_keyword` field
    for kw in sorted_keywords:
        del kw['condensed_keyword']

    return {'keywords': sorted_keywords}

def main():
    # Get list of feature files from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python script.py feature_file1.feature feature_file2.feature ... keyword_list.json")
        sys.exit(1)
    
    feature_files = sys.argv[1:-1]
    output_file = sys.argv[-1]

    # Process the files and get the keywords
    result = process_feature_files(feature_files)
    
    # Write the result to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
