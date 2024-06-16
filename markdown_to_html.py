import argparse
import markdown
import json
from jinja2 import Template
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_file(file_path):
    logging.info(f"reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"file not found: {file_path}")
        return None

def convert_markdown_to_html(markdown_content):
    logging.info("converting markdown to HTML")
    return markdown.markdown(markdown_content, extensions=['toc'])

def write_file(file_path, content):
    logging.info(f"writing to file: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_metadata(markdown_content):
    logging.info("extracting metadata from markdown")
    metadata = {}
    lines = markdown_content.split('\n')
    metadata_pattern = re.compile(r'^\s*([A-Za-z0-9-_]+):\s*(.+)\s*$')
    for line in lines:
        match = metadata_pattern.match(line)
        if match:
            key, value = match.groups()
            metadata[key.strip()] = value.strip()
    logging.info(f"metadata extracted: {metadata}")
    return metadata

def generate_toc(html_content):
    logging.info("generating table of contents")
    toc = []
    heading_pattern = re.compile(r'<h([1-6])>(.*?)</h\1>')
    matches = heading_pattern.findall(html_content)
    for level, title in matches:
        anchor = re.sub(r'\s+', '-', title.lower())
        toc.append({'title': title, 'anchor': anchor})
        html_content = html_content.replace(f'<h{level}>{title}</h{level}>', f'<h{level} id="{anchor}">{title}</h{level}>')
    return toc, html_content

def apply_template(html_content, metadata, toc, template_path, css_content=None):
    logging.info("applying HTML template")
    template_str = read_file(template_path)
    template = Template(template_str)
    return template.render(html_content=html_content, css_content=css_content, toc=toc, **metadata)

def main():
    parser = argparse.ArgumentParser(description='convert markdown to HTML')
    parser.add_argument('input', help='input markdown file')
    parser.add_argument('output', help='output HTML file')
    parser.add_argument('--css', help='optional CSS file for styling', default=None)
    parser.add_argument('--template', help='optional HTML template file', default='templates/default_template.html')
    parser.add_argument('--config', help='optional configuration file', default='config.json')
    args = parser.parse_args()

    config = {}
    if os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info(f"loaded configuration from {args.config}")

    input_file = args.input
    output_file = args.output
    css_file = args.css or config.get('css')
    template_file = args.template or config.get('template', 'templates/default_template.html')

    markdown_content = read_file(input_file)
    if markdown_content is None:
        return
    
    metadata = extract_metadata(markdown_content)
    html_content = convert_markdown_to_html(markdown_content)
    toc, html_content = generate_toc(html_content)

    css_content = None
    if css_file:
        css_content = read_file(css_file)
        if css_content is None:
            return
        
    final_html = apply_template(html_content, metadata, toc, template_file, css_content)
    write_file(output_file, final_html)
    logging.info("conversion successful")

if __name__ == "__main__":
    main()