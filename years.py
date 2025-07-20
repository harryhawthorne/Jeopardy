import os
import json
import re
from collections import Counter, defaultdict
import pandas as pd
import plotly.express as px
import logging
import textwrap

# --- Configuration ---
CONFIG = {
    "BASE_DATA_PATH": "data/",
    "OUTPUT_HTML_FILE": "charts/jeopardy_year_frequency_clues.html",
    "START_YEAR": 1400,
    "END_YEAR": 2025
}

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_all_game_files(base_path):
    """Recursively finds all .json game files in the base data directory."""
    json_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def aggregate_year_mentions(game_files):
    """
    Aggregates the frequency of years and collects the associated clues for each year,
    excluding years explicitly marked as B.C.
    """
    year_counts = Counter()
    year_clues = defaultdict(list)

    logging.info(f"Processing {len(game_files)} game files to find year mentions and clues...")
    
    # MODIFIED: This regex finds a 4-digit number that is NOT followed by "B.C." or "BC"
    pattern = r'\b(\d{4})\b(?!\s*B\.?\s*C\.?)'

    for file_path in game_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for round_data in data.get("rounds", []):
                for category in round_data.get("categories", []):
                    category_name = category.get("name", "N/A")
                    for clue in category.get("clues", []):
                        clue_text = clue.get("clue", "")
                        
                        # Find all valid years in the clue using the new pattern
                        valid_years = re.findall(pattern, clue_text, re.IGNORECASE)
                        
                        for year_str in valid_years:
                            year_int = int(year_str)
                            if CONFIG["START_YEAR"] <= year_int <= CONFIG["END_YEAR"]:
                                year_counts[year_int] += 1
                                year_clues[year_int].append({
                                    "clue": clue.get("clue", "N/A"),
                                    "answer": clue.get("answer", "N/A"),
                                    "category": category_name
                                })
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Skipping malformed file {file_path}: {e}")
            continue
            
    return year_counts, year_clues

def plot_year_frequency(year_counts, year_clues):
    """
    Creates and saves a bar chart with detailed, category-inclusive clue information in the hover labels.
    """
    if not year_counts:
        logging.warning("No year data to plot.")
        return

    df = pd.DataFrame(year_counts.items(), columns=['Year', 'Frequency']).sort_values(by='Year')

    hover_texts = []
    for index, row in df.iterrows():
        year = row['Year']
        frequency = row['Frequency']
        header = f"<b>{year}</b>: {frequency}"
        
        clues_preview = year_clues.get(year, [])[:5]
        
        clue_strings = []
        for item in clues_preview:
            category_text = item.get('category', 'N/A')
            clue_text = item.get('clue', 'N/A')
            answer_text = item.get('answer', 'N/A')
            
            wrapped_clue = textwrap.fill(clue_text, width=80).replace('\n', '<br>')
            
            full_line = f"<b>{category_text}</b>: {wrapped_clue}: <i>{answer_text}</i>"
            clue_strings.append(full_line)
        
        clue_details = "<br>".join(clue_strings)
        
        if clue_details:
            hover_text = f"{header}<br>-----------------------------<br>{clue_details}"
        else:
            hover_text = header
            
        hover_texts.append(hover_text)
    
    df['hover_text'] = hover_texts

    logging.info(f"Generating bar chart for {len(df)} unique years...")
    
    fig = px.bar(
        df,
        x='Year',
        y='Frequency',
        custom_data=['hover_text'],
        title=f'Frequency of Years Mentioned in Jeopardy! Clues',
        labels={'Year': 'Year Mentioned in Clue', 'Frequency': 'Number of Mentions'}
    )
    
    fig.update_traces(hovertemplate='%{customdata}<extra></extra>')
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='lightgrey'), 
        yaxis=dict(gridcolor='lightgrey'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            align="left"
        )
    )

    fig.write_html(CONFIG['OUTPUT_HTML_FILE'])
    logging.info(f"Success! Open '{CONFIG['OUTPUT_HTML_FILE']}' in your browser to view the chart.")

if __name__ == "__main__":
    game_files = get_all_game_files(CONFIG['BASE_DATA_PATH'])
    year_counts, year_clues = aggregate_year_mentions(game_files)
    plot_year_frequency(year_counts, year_clues)