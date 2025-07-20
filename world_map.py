import os
import json
import pandas as pd
import plotly.express as px
from collections import defaultdict
import pycountry
import textwrap

def get_country_counts():
    """
    Parses Jeopardy data, mapping all country name variations to a standard
    3-letter ISO code for reliable plotting.
    """
    country_counts = defaultdict(int)
    country_clues = defaultdict(list)
    
    name_map = {}
    for country in pycountry.countries:
        name_map[country.name] = country.alpha_3
        if hasattr(country, 'common_name'):
            name_map[country.common_name] = country.alpha_3
        if hasattr(country, 'official_name'):
            name_map[country.official_name] = country.alpha_3

    manual_aliases = {
        # General Aliases
        'Turkey': 'TUR',
        'Türkiye': 'TUR',
        'Russia': 'RUS',
        'U.S.A.': 'USA',
        'USA': 'USA',
        'The United States': 'USA',
        'Great Britain': 'GBR',
        'UK': 'GBR',
        'England': 'GBR',
        'Holland': 'NLD',
        'South Korea': 'KOR',
        'North Korea': 'PRK',
        'Vietnam': 'VNM',
        'The Vatican': 'VAT',
        'Vatican City': 'VAT',
        'Soviet Union': 'RUS',
        'U.S.S.R.': 'RUS',
        'USSR': 'RUS',
        'Swaziland': 'SWZ',
        'Zaire': 'COD',
        'DRC': 'COD',
        'DR Congo': 'COD',
        'Congo, Democratic Republic of the': 'COD',
    }
    name_map.update(manual_aliases)

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
                                            iso_code = name_map[answer]
                                            country_counts[iso_code] += 1
                                            if len(country_clues[iso_code]) < 5:
                                                clue_info = {
                                                    'category': category_name,
                                                    'clue': clue.get('clue', '')
                                                }
                                                country_clues[iso_code].append(clue_info)
                        except (json.JSONDecodeError, KeyError) as e:
                            print(f"Skipping file {episode_file} due to error: {e}")
                            continue
    return country_counts, country_clues

def create_world_map(country_counts, country_clues):
    """
    Creates the world map using ISO-3 codes for location and wraps hover text.
    """
    iso_codes = list(country_counts.keys())
    counts = list(country_counts.values())
    
    iso_to_name = {country.alpha_3: country.name for country in pycountry.countries}

    hover_texts = []
    for iso_code in iso_codes:
        country_name = iso_to_name.get(iso_code, iso_code)
        
        clues_list = []
        for item in country_clues[iso_code]:
            category = item.get('category', 'N/A')
            clue = item.get('clue', '')
            
            wrapped_clue = textwrap.fill(clue, width=70).replace('\n', '<br>')
            clues_list.append(f"<b>{category}</b>: {wrapped_clue}")
        
        clues_html = "<br><br>".join(clues_list)
        
        hover_text = (
            f"<b>{country_name}</b>: {country_counts[iso_code]}<br><br>{clues_html}"
        )
        hover_texts.append(hover_text)

    data = {
        'iso_code': iso_codes,
        'country_name': [iso_to_name.get(code, code) for code in iso_codes],
        'count': counts,
        'hover_text': hover_texts
    }
    df = pd.DataFrame(data)

    fig = px.choropleth(
        df,
        locations="iso_code",
        locationmode="ISO-3",
        color="count",
        hover_name="country_name",
        custom_data=['hover_text'],
        color_continuous_scale=['#FFFFFF', '#070973'], # MODIFIED: Custom color scale
    )
    
    fig.update_traces(hovertemplate='%{customdata}<extra></extra>')
    
    # MODIFIED: Simplified layout for a clean, white theme
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

    fig.write_html("charts/jeopardy_answers_by_country.html")
    print("Map has been generated and saved as charts/jeopardy_answers_by_country.html")


if __name__ == "__main__":
    print("Analyzing Jeopardy data...")
    country_counts, country_clues = get_country_counts()
    print("Generating world map...")
    create_world_map(country_counts, country_clues)