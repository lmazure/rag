import json
import sys
from typing import List, Dict
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner
from gherkin.token_matcher import TokenMatcher

def extract_keywords(file_path: str) -> List[Dict[str, str]]:
    """
    Extract Gherkin keywords from a single feature file using gherkin-official parser.
    Returns a list of dictionaries containing keyword type and text.
    """
    keywords = []
    parser = Parser()
    
    try:
        # Read the feature file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the feature file
        feature_file = parser.parse(TokenScanner(content))
        
        # Process each feature
        for feature in feature_file['feature']['children']:
            # Process background if it exists
            if feature.get('type') == 'Background':
                for step in feature.get('steps', []):
                    step_type = step['keyword'].strip()
                    if step_type in ['And ', 'But ']:  # Note: Gherkin parser keeps the space
                        if keywords:
                            step_type = keywords[-1]['type']
                        else:
                            continue
                    else:
                        step_type = step_type.strip()  # Remove trailing space
                    
                    keywords.append({
                        'type': step_type,
                        'keyword': step['text'].strip()
                    })
            
            # Process scenarios and scenario outlines
            elif feature.get('type') in ['Scenario', 'ScenarioOutline']:
                for step in feature.get('steps', []):
                    step_type = step['keyword'].strip()
                    if step_type in ['And ', 'But ']:  # Note: Gherkin parser keeps the space
                        if keywords:
                            step_type = keywords[-1]['type']
                        else:
                            continue
                    else:
                        step_type = step_type.strip()  # Remove trailing space
                    
                    keywords.append({
                        'type': step_type,
                        'keyword': step['text'].strip()
                    })
                    
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
    
    return keywords

def sort_keywords(keywords: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sort keywords first by type (Given, When, Then) then alphabetically by keyword text.
    """
    # Define the order of keyword types
    type_order = {'Given': 1, 'When': 2, 'Then': 3}
    
    # Sort the keywords
    return sorted(
        keywords,
        key=lambda x: (
            type_order.get(x['type'], 999),  # First sort by type (using 999 for unknown types)
            x['keyword'].lower()              # Then sort alphabetically (case-insensitive)
        )
    )

def process_feature_files(file_paths: List[str]) -> Dict:
    """
    Process multiple feature files and return a dictionary with unique, sorted keywords.
    """
    all_keywords = []
    unique_keywords = set()
    
    for file_path in file_paths:
        if file_path.endswith('.feature'):
            keywords = extract_keywords(file_path)
            
            # Add only unique keywords
            for kw in keywords:
                # Create a tuple of type and keyword for uniqueness check
                kw_tuple = (kw['type'], kw['keyword'])
                if kw_tuple not in unique_keywords:
                    unique_keywords.add(kw_tuple)
                    all_keywords.append(kw)
    
    # Sort the keywords
    sorted_keywords = sort_keywords(all_keywords)
    
    return {'keywords': sorted_keywords}

def main():
    # Get list of feature files from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python script.py feature_file1.feature feature_file2.feature ...")
        sys.exit(1)
    
    feature_files = sys.argv[1:]
    
    # Process the files and get the keywords
    result = process_feature_files(feature_files)
    
    # Write the result to a JSON file
    output_file = 'jenkins_keywords.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"Keywords have been extracted and saved to {output_file}")

if __name__ == "__main__":
    main()
