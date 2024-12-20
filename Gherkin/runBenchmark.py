import argparse
import csv
import html
from queryDatabase import extract_keywords

def process_file(file_path, models, db_path, nb_results):
    results = {}
    index = 1
    
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)  # Skip header row
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            
            keyword_type, keyword, expected_id = row
            search_results = {}
            
            for model in models:
                model_results = extract_keywords(db_path, model, keyword_type, keyword, nb_results)
                search_results[model] = { 'matches': model_results, 'success': [result['id'] for result in model_results].index(expected_id) if expected_id in [result['id'] for result in model_results] else -1 }
            
            results[index] = {
                'keyword': keyword,
                'results': search_results
            }
            index += 1
    return results



def generate_html(file_path, results):
    # Get unique list of models
    all_models = set()
    for data in results.values():
        all_models.update(data['results'].keys())
    all_models = sorted(all_models)

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Benchmark results</title>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .model-header { text-align: center; }
            .matches { max-width: 300px; overflow-wrap: break-word; }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th rowspan="2">ID</th>
                <th rowspan="2">Keyword</th>
    """
    
    # Add model names as column headers
    for model in all_models:
        html_content += f'<th colspan="2" class="model-header">{html.escape(model)}</th>'
    
    html_content += "</tr><tr>"
    
    # Add subcolumn headers for each model
    for _ in all_models:
        html_content += "<th>Matches</th><th>Success</th>"
    
    html_content += "</tr>"

    for id, data in results.items():
        html_content += f"""
        <tr>
            <td>{id}</td>
            <td>{html.escape(data['keyword'])}</td>
        """
        
        for model in all_models:
            if model in data['results']:
                model_results = data['results'][model]
                matches = "<br>".join([f"{match['id']}: {html.escape(match['keyword'])} {match['distance']:.2f} {'😊' if i == model_results['success'] else ''}" for i, match in enumerate(model_results['matches'])])
                success = "✔️" if (model_results['success'] >= 0) else '❌️'
                html_content += f'<td class="matches">{matches}</td><td>{success}</td>'
            else:
                html_content += '<td>N/A</td><td>N/A</td>'
        
        html_content += "</tr>"

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description="Process keywords using multiple models and Chroma database.")
    parser.add_argument("--models", required=True, help="Comma-separated list of the names of the models to evaluate")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--nb_results", default=3, type=int, required=True, help="Number of matches to consider (default: 3)")
    parser.add_argument("benchmark_file", help="Path to the benchmark definition file")
    parser.add_argument("report_file", help="Path to the HTML report file to generate")

    args = parser.parse_args()
    
    models = [model.strip() for model in args.models.split(',')]
    
    # Run benchmark
    results = process_file(args.benchmark_file, models, args.db_path, args.nb_results)
    
    # Generate HTML report
    generate_html(args.report_file, results)

if __name__ == "__main__":
    main()
