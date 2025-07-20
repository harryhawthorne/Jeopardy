import os
import json
import pandas as pd
import plotly.express as px
from collections import defaultdict
import textwrap

def get_state_data():
    """
    Returns a dictionary mapping full US state names to their 2-letter postal codes.
    This replaces the pycountry library for the US map.
    """
    states = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
        'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
        'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
    }
    return states

def get_state_counts():
    """
    Parses Jeopardy data to count how many times each US state is an answer.
    """
    state_counts = defaultdict(int)
    state_clues = defaultdict(list)
    
    # Create a name map from the full state name to its 2-letter code
    name_map = get_state_data()

    for season_dir in os.listdir('data'):
        season_path = os.path.join('data', season_dir)
        if os.path.isdir(season_path):
            for episode_file in os.listdir(season_path):
                if episode_file.endswith('.json'):
                    with open(os.path.join(season_path, episode_file), 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            for round_data in data.get('rounds', []):
                                for category in round_data.get('categories', []):
                                    category_name = category.get('name', 'N/A')
                                    for clue in category.get('clues', []):
                                        answer = clue.get('answer', '')
                                        if answer in name_map:
                                            state_code = name_map[answer]
                                            state_counts[state_code] += 1
                                            if len(state_clues[state_code]) < 5:
                                                clue_info = {
                                                    'category': category_name,
                                                    'clue': clue.get('clue', '')
                                                }
                                                state_clues[state_code].append(clue_info)
                        except (json.JSONDecodeError, KeyError) as e:
                            print(f"Skipping file {episode_file} due to error: {e}")
                            continue
    return state_counts, state_clues

def create_us_map(state_counts, state_clues):
    """
    Creates the US map using 2-letter state codes for location and wraps hover text.
    """
    state_codes = list(state_counts.keys())
    counts = list(state_counts.values())
    
    # Create a mapping from 2-letter code back to the full state name for display
    state_data = get_state_data()
    code_to_name = {v: k for k, v in state_data.items()}

    hover_texts = []
    for state_code in state_codes:
        state_name = code_to_name.get(state_code, state_code)
        
        clues_list = []
        for item in state_clues[state_code]:
            category = item.get('category', 'N/A')
            clue = item.get('clue', '')
            
            wrapped_clue = textwrap.fill(clue, width=70).replace('\n', '<br>')
            clues_list.append(f"<b>{category}</b>: {wrapped_clue}")
        
        clues_html = "<br><br>".join(clues_list)
        
        hover_text = (
            f"<b>{state_name}</b>: {state_counts[state_code]}<br><br>{clues_html}"
        )
        hover_texts.append(hover_text)

    data = {
        'state_code': state_codes,
        'state_name': [code_to_name.get(code, code) for code in state_codes],
        'count': counts,
        'hover_text': hover_texts
    }
    df = pd.DataFrame(data)

    fig = px.choropleth(
        df,
        locations="state_code",
        locationmode="USA-states",
        scope="usa",
        color="count",
        hover_name="state_name",
        custom_data=['hover_text'],
        color_continuous_scale=['#FFFFFF', '#070973'],
    )
    
    fig.update_traces(hovertemplate='%{customdata}<extra></extra>')
    
    fig.update_layout(
        paper_bgcolor='white',
        geo=dict(
            bgcolor='white',
            lakecolor='white'
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        )
    )

    fig.write_html("charts/jeopardy_answers_by_state.html")
    print("Map has been generated and saved as charts/jeopardy_answers_by_state.html")


if __name__ == "__main__":
    print("Analyzing Jeopardy data for US states...")
    state_counts, state_clues = get_state_counts()
    print("Generating US map...")
    create_us_map(state_counts, state_clues)