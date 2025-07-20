import os
import json
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
import textwrap

def get_element_data():
    """
    Returns a hardcoded list of dictionaries with all element data.
    This removes the need for the problematic 'periodictable' external library.
    """
    # Data source: https://gist.github.com/GoodmanSciences/c2dd862cd38f21b0ad36
    return [
        {'number': 1, 'symbol': 'H', 'name': 'Hydrogen', 'period': 1, 'group': 1},
        {'number': 2, 'symbol': 'He', 'name': 'Helium', 'period': 1, 'group': 18},
        {'number': 3, 'symbol': 'Li', 'name': 'Lithium', 'period': 2, 'group': 1},
        {'number': 4, 'symbol': 'Be', 'name': 'Beryllium', 'period': 2, 'group': 2},
        {'number': 5, 'symbol': 'B', 'name': 'Boron', 'period': 2, 'group': 13},
        {'number': 6, 'symbol': 'C', 'name': 'Carbon', 'period': 2, 'group': 14},
        {'number': 7, 'symbol': 'N', 'name': 'Nitrogen', 'period': 2, 'group': 15},
        {'number': 8, 'symbol': 'O', 'name': 'Oxygen', 'period': 2, 'group': 16},
        {'number': 9, 'symbol': 'F', 'name': 'Fluorine', 'period': 2, 'group': 17},
        {'number': 10, 'symbol': 'Ne', 'name': 'Neon', 'period': 2, 'group': 18},
        {'number': 11, 'symbol': 'Na', 'name': 'Sodium', 'period': 3, 'group': 1},
        {'number': 12, 'symbol': 'Mg', 'name': 'Magnesium', 'period': 3, 'group': 2},
        {'number': 13, 'symbol': 'Al', 'name': 'Aluminium', 'period': 3, 'group': 13},
        {'number': 14, 'symbol': 'Si', 'name': 'Silicon', 'period': 3, 'group': 14},
        {'number': 15, 'symbol': 'P', 'name': 'Phosphorus', 'period': 3, 'group': 15},
        {'number': 16, 'symbol': 'S', 'name': 'Sulfur', 'period': 3, 'group': 16},
        {'number': 17, 'symbol': 'Cl', 'name': 'Chlorine', 'period': 3, 'group': 17},
        {'number': 18, 'symbol': 'Ar', 'name': 'Argon', 'period': 3, 'group': 18},
        {'number': 19, 'symbol': 'K', 'name': 'Potassium', 'period': 4, 'group': 1},
        {'number': 20, 'symbol': 'Ca', 'name': 'Calcium', 'period': 4, 'group': 2},
        {'number': 21, 'symbol': 'Sc', 'name': 'Scandium', 'period': 4, 'group': 3},
        {'number': 22, 'symbol': 'Ti', 'name': 'Titanium', 'period': 4, 'group': 4},
        {'number': 23, 'symbol': 'V', 'name': 'Vanadium', 'period': 4, 'group': 5},
        {'number': 24, 'symbol': 'Cr', 'name': 'Chromium', 'period': 4, 'group': 6},
        {'number': 25, 'symbol': 'Mn', 'name': 'Manganese', 'period': 4, 'group': 7},
        {'number': 26, 'symbol': 'Fe', 'name': 'Iron', 'period': 4, 'group': 8},
        {'number': 27, 'symbol': 'Co', 'name': 'Cobalt', 'period': 4, 'group': 9},
        {'number': 28, 'symbol': 'Ni', 'name': 'Nickel', 'period': 4, 'group': 10},
        {'number': 29, 'symbol': 'Cu', 'name': 'Copper', 'period': 4, 'group': 11},
        {'number': 30, 'symbol': 'Zn', 'name': 'Zinc', 'period': 4, 'group': 12},
        {'number': 31, 'symbol': 'Ga', 'name': 'Gallium', 'period': 4, 'group': 13},
        {'number': 32, 'symbol': 'Ge', 'name': 'Germanium', 'period': 4, 'group': 14},
        {'number': 33, 'symbol': 'As', 'name': 'Arsenic', 'period': 4, 'group': 15},
        {'number': 34, 'symbol': 'Se', 'name': 'Selenium', 'period': 4, 'group': 16},
        {'number': 35, 'symbol': 'Br', 'name': 'Bromine', 'period': 4, 'group': 17},
        {'number': 36, 'symbol': 'Kr', 'name': 'Krypton', 'period': 4, 'group': 18},
        {'number': 37, 'symbol': 'Rb', 'name': 'Rubidium', 'period': 5, 'group': 1},
        {'number': 38, 'symbol': 'Sr', 'name': 'Strontium', 'period': 5, 'group': 2},
        {'number': 39, 'symbol': 'Y', 'name': 'Yttrium', 'period': 5, 'group': 3},
        {'number': 40, 'symbol': 'Zr', 'name': 'Zirconium', 'period': 5, 'group': 4},
        {'number': 41, 'symbol': 'Nb', 'name': 'Niobium', 'period': 5, 'group': 5},
        {'number': 42, 'symbol': 'Mo', 'name': 'Molybdenum', 'period': 5, 'group': 6},
        {'number': 43, 'symbol': 'Tc', 'name': 'Technetium', 'period': 5, 'group': 7},
        {'number': 44, 'symbol': 'Ru', 'name': 'Ruthenium', 'period': 5, 'group': 8},
        {'number': 45, 'symbol': 'Rh', 'name': 'Rhodium', 'period': 5, 'group': 9},
        {'number': 46, 'symbol': 'Pd', 'name': 'Palladium', 'period': 5, 'group': 10},
        {'number': 47, 'symbol': 'Ag', 'name': 'Silver', 'period': 5, 'group': 11},
        {'number': 48, 'symbol': 'Cd', 'name': 'Cadmium', 'period': 5, 'group': 12},
        {'number': 49, 'symbol': 'In', 'name': 'Indium', 'period': 5, 'group': 13},
        {'number': 50, 'symbol': 'Sn', 'name': 'Tin', 'period': 5, 'group': 14},
        {'number': 51, 'symbol': 'Sb', 'name': 'Antimony', 'period': 5, 'group': 15},
        {'number': 52, 'symbol': 'Te', 'name': 'Tellurium', 'period': 5, 'group': 16},
        {'number': 53, 'symbol': 'I', 'name': 'Iodine', 'period': 5, 'group': 17},
        {'number': 54, 'symbol': 'Xe', 'name': 'Xenon', 'period': 5, 'group': 18},
        {'number': 55, 'symbol': 'Cs', 'name': 'Caesium', 'period': 6, 'group': 1},
        {'number': 56, 'symbol': 'Ba', 'name': 'Barium', 'period': 6, 'group': 2},
        {'number': 57, 'symbol': 'La', 'name': 'Lanthanum', 'period': 6, 'group': 3},
        {'number': 58, 'symbol': 'Ce', 'name': 'Cerium', 'period': 6, 'group': 3},
        {'number': 59, 'symbol': 'Pr', 'name': 'Praseodymium', 'period': 6, 'group': 3},
        {'number': 60, 'symbol': 'Nd', 'name': 'Neodymium', 'period': 6, 'group': 3},
        {'number': 61, 'symbol': 'Pm', 'name': 'Promethium', 'period': 6, 'group': 3},
        {'number': 62, 'symbol': 'Sm', 'name': 'Samarium', 'period': 6, 'group': 3},
        {'number': 63, 'symbol': 'Eu', 'name': 'Europium', 'period': 6, 'group': 3},
        {'number': 64, 'symbol': 'Gd', 'name': 'Gadolinium', 'period': 6, 'group': 3},
        {'number': 65, 'symbol': 'Tb', 'name': 'Terbium', 'period': 6, 'group': 3},
        {'number': 66, 'symbol': 'Dy', 'name': 'Dysprosium', 'period': 6, 'group': 3},
        {'number': 67, 'symbol': 'Ho', 'name': 'Holmium', 'period': 6, 'group': 3},
        {'number': 68, 'symbol': 'Er', 'name': 'Erbium', 'period': 6, 'group': 3},
        {'number': 69, 'symbol': 'Tm', 'name': 'Thulium', 'period': 6, 'group': 3},
        {'number': 70, 'symbol': 'Yb', 'name': 'Ytterbium', 'period': 6, 'group': 3},
        {'number': 71, 'symbol': 'Lu', 'name': 'Lutetium', 'period': 6, 'group': 3},
        {'number': 72, 'symbol': 'Hf', 'name': 'Hafnium', 'period': 6, 'group': 4},
        {'number': 73, 'symbol': 'Ta', 'name': 'Tantalum', 'period': 6, 'group': 5},
        {'number': 74, 'symbol': 'W', 'name': 'Tungsten', 'period': 6, 'group': 6},
        {'number': 75, 'symbol': 'Re', 'name': 'Rhenium', 'period': 6, 'group': 7},
        {'number': 76, 'symbol': 'Os', 'name': 'Osmium', 'period': 6, 'group': 8},
        {'number': 77, 'symbol': 'Ir', 'name': 'Iridium', 'period': 6, 'group': 9},
        {'number': 78, 'symbol': 'Pt', 'name': 'Platinum', 'period': 6, 'group': 10},
        {'number': 79, 'symbol': 'Au', 'name': 'Gold', 'period': 6, 'group': 11},
        {'number': 80, 'symbol': 'Hg', 'name': 'Mercury', 'period': 6, 'group': 12},
        {'number': 81, 'symbol': 'Tl', 'name': 'Thallium', 'period': 6, 'group': 13},
        {'number': 82, 'symbol': 'Pb', 'name': 'Lead', 'period': 6, 'group': 14},
        {'number': 83, 'symbol': 'Bi', 'name': 'Bismuth', 'period': 6, 'group': 15},
        {'number': 84, 'symbol': 'Po', 'name': 'Polonium', 'period': 6, 'group': 16},
        {'number': 85, 'symbol': 'At', 'name': 'Astatine', 'period': 6, 'group': 17},
        {'number': 86, 'symbol': 'Rn', 'name': 'Radon', 'period': 6, 'group': 18},
        {'number': 87, 'symbol': 'Fr', 'name': 'Francium', 'period': 7, 'group': 1},
        {'number': 88, 'symbol': 'Ra', 'name': 'Radium', 'period': 7, 'group': 2},
        {'number': 89, 'symbol': 'Ac', 'name': 'Actinium', 'period': 7, 'group': 3},
        {'number': 90, 'symbol': 'Th', 'name': 'Thorium', 'period': 7, 'group': 3},
        {'number': 91, 'symbol': 'Pa', 'name': 'Protactinium', 'period': 7, 'group': 3},
        {'number': 92, 'symbol': 'U', 'name': 'Uranium', 'period': 7, 'group': 3},
        {'number': 93, 'symbol': 'Np', 'name': 'Neptunium', 'period': 7, 'group': 3},
        {'number': 94, 'symbol': 'Pu', 'name': 'Plutonium', 'period': 7, 'group': 3},
        {'number': 95, 'symbol': 'Am', 'name': 'Americium', 'period': 7, 'group': 3},
        {'number': 96, 'symbol': 'Cm', 'name': 'Curium', 'period': 7, 'group': 3},
        {'number': 97, 'symbol': 'Bk', 'name': 'Berkelium', 'period': 7, 'group': 3},
        {'number': 98, 'symbol': 'Cf', 'name': 'Californium', 'period': 7, 'group': 3},
        {'number': 99, 'symbol': 'Es', 'name': 'Einsteinium', 'period': 7, 'group': 3},
        {'number': 100, 'symbol': 'Fm', 'name': 'Fermium', 'period': 7, 'group': 3},
        {'number': 101, 'symbol': 'Md', 'name': 'Mendelevium', 'period': 7, 'group': 3},
        {'number': 102, 'symbol': 'No', 'name': 'Nobelium', 'period': 7, 'group': 3},
        {'number': 103, 'symbol': 'Lr', 'name': 'Lawrencium', 'period': 7, 'group': 3},
        {'number': 104, 'symbol': 'Rf', 'name': 'Rutherfordium', 'period': 7, 'group': 4},
        {'number': 105, 'symbol': 'Db', 'name': 'Dubnium', 'period': 7, 'group': 5},
        {'number': 106, 'symbol': 'Sg', 'name': 'Seaborgium', 'period': 7, 'group': 6},
        {'number': 107, 'symbol': 'Bh', 'name': 'Bohrium', 'period': 7, 'group': 7},
        {'number': 108, 'symbol': 'Hs', 'name': 'Hassium', 'period': 7, 'group': 8},
        {'number': 109, 'symbol': 'Mt', 'name': 'Meitnerium', 'period': 7, 'group': 9},
        {'number': 110, 'symbol': 'Ds', 'name': 'Darmstadtium', 'period': 7, 'group': 10},
        {'number': 111, 'symbol': 'Rg', 'name': 'Roentgenium', 'period': 7, 'group': 11},
        {'number': 112, 'symbol': 'Cn', 'name': 'Copernicium', 'period': 7, 'group': 12},
        {'number': 113, 'symbol': 'Nh', 'name': 'Nihonium', 'period': 7, 'group': 13},
        {'number': 114, 'symbol': 'Fl', 'name': 'Flerovium', 'period': 7, 'group': 14},
        {'number': 115, 'symbol': 'Mc', 'name': 'Moscovium', 'period': 7, 'group': 15},
        {'number': 116, 'symbol': 'Lv', 'name': 'Livermorium', 'period': 7, 'group': 16},
        {'number': 117, 'symbol': 'Ts', 'name': 'Tennessine', 'period': 7, 'group': 17},
        {'number': 118, 'symbol': 'Og', 'name': 'Oganesson', 'period': 7, 'group': 18}
    ]

def get_element_counts():
    """
    Parses Jeopardy data to count how many times each element is an answer.
    """
    element_counts = defaultdict(int)
    element_clues = defaultdict(list)
    
    name_map = {}
    for el in get_element_data():
        name_map[el['name']] = el['symbol']
        name_map[el['symbol']] = el['symbol']

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
                                        answer = clue.get('answer', '').title()
                                        if answer in name_map:
                                            element_symbol = name_map[answer]
                                            element_counts[element_symbol] += 1
                                            if len(element_clues[element_symbol]) < 5:
                                                clue_info = {
                                                    'category': category_name,
                                                    'clue': clue.get('clue', '')
                                                }
                                                element_clues[element_symbol].append(clue_info)
                        except (json.JSONDecodeError, KeyError) as e:
                            print(f"Skipping file {episode_file} due to error: {e}")
                            continue
    return element_counts, element_clues

def create_periodic_table_plot(element_counts, element_clues):
    """
    Creates an interactive periodic table visualization.
    """
    plot_data = []
    # Loop through the hardcoded element data to build the table structure
    for el in get_element_data():
        # Position Lanthanides and Actinides below the main table
        if 57 <= el['number'] <= 71:  # Lanthanides
            x_pos = el['number'] - 57 + 3
            y_pos = 8.5
        elif 89 <= el['number'] <= 103:  # Actinides
            x_pos = el['number'] - 89 + 3
            y_pos = 9.5
        else:
            x_pos = el['group']
            y_pos = el['period']

        count = element_counts.get(el['symbol'], 0)
        
        # Build hover text
        clues_list = []
        for item in element_clues.get(el['symbol'], []):
            category = item.get('category', 'N/A')
            clue = item.get('clue', '')
            wrapped_clue = textwrap.fill(clue, width=70).replace('\n', '<br>')
            clues_list.append(f"<b>{category}</b>: {wrapped_clue}")
        clues_html = "<br><br>".join(clues_list)
        hover_text = f"<b>{el['name']} ({el['symbol']})</b><br>Count: {count}<br><br>{clues_html}"

        plot_data.append({
            'x': x_pos,
            'y': y_pos,
            'symbol': el['symbol'],
            'name': el['name'],
            'number': el['number'],
            'count': count,
            'hover_text': hover_text
        })

    df = pd.DataFrame(plot_data)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['x'],
        y=df['y'],
        mode='markers+text',
        text=df['symbol'],
        customdata=df['hover_text'],
        hovertemplate='%{customdata}<extra></extra>',
        marker=dict(
            symbol='square',
            size=40,  # <-- REDUCED MARKER SIZE
            color=df['count'],
            colorscale=['#FFFFFF', '#070973'],
            showscale=True,
            colorbar=dict(
                title="Count",
                thickness=20,
                x=1.02,
                xanchor='left'
            ),
        ),
        textfont=dict(
            family="sans-serif",
            size=14,
            color="black"
        )
    ))
    
    fig.update_layout(
        xaxis=dict(
            range=[0, 19],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[10, 0.5],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        )
    )

    fig.write_html("charts/jeopardy_answers_by_element.html")
    print("Periodic table saved to charts/jeopardy_answers_by_element.html")

if __name__ == "__main__":
    print("Analyzing Jeopardy data for chemical elements...")
    element_counts, element_clues = get_element_counts()
    print("Generating periodic table...")
    create_periodic_table_plot(element_counts, element_clues)