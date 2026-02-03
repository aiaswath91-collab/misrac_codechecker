from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from typing import Dict
from collections import defaultdict


def generate_html_report(results: Dict, output_path: str, project_name: str):
    """Generate standalone HTML report"""
    
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("misra_report.html.j2")
    
    violations = results.get('violations', [])
    summary = results.get('summary', {})
    
    file_violations = defaultdict(list)
    for v in violations:
        file_violations[v['file']].append(v)
    
    context = {
        'project_name': project_name,
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': summary,
        'file_stats': summary.get('file_stats', {}),
        'file_violations': dict(file_violations),
        'all_files': sorted(file_violations.keys())
    }
    
    html_content = template.render(**context)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
