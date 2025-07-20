import os
import json
import pandas as pd
import plotly.express as px
from collections import Counter

def analyze_answer_frequencies(data_path):
    """
    Analyzes all seasons to find the frequency of each full answer per season.
    """
    season_answer_counts = {}
    for season_dir in sorted(os.listdir(data_path)):
        season_path = os.path.join(data_path, season_dir)
        if os.path.isdir(season_path):
            try:
                season_num = int(os.path.basename(season_dir))
                season_answers = []
                for episode_file in os.listdir(season_path):
                    if episode_file.endswith('.json'):
                        with open(os.path.join(season_path, episode_file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for round_data in data.get('rounds', []):
                                for category in round_data.get('categories', []):
                                    for clue in category.get('clues', []):
                                        answer = clue.get('answer', '').strip().title()
                                        if answer and answer != "=":
                                            season_answers.append(answer)
                season_answer_counts[season_num] = Counter(season_answers)
            except (json.JSONDecodeError, ValueError, KeyError):
                continue
    return season_answer_counts

def process_ranks(season_answer_counts, top_n=20):
    """
    Processes answer counts to calculate ranks and prepares data for plotting,
    including a pre-formatted hover text string.
    """
    top_answers = set()
    for season, counts in season_answer_counts.items():
        top_answers.update([answer for answer, count in counts.most_common(top_n)])

    plot_data = []
    appearance_counts = Counter()
    for season, counts in season_answer_counts.items():
        ranked_answers = [answer for answer, count in counts.most_common()]
        for answer in top_answers:
            rank = None
            count = counts.get(answer, 0)
            try:
                calculated_rank = ranked_answers.index(answer) + 1
                if calculated_rank <= top_n:
                    rank = calculated_rank
                    appearance_counts[answer] += 1
            except ValueError:
                pass
            
            hover_text = f"<b>{answer}</b><br>Rank: {rank if rank is not None else 'N/A'}<br>Count: {count}"
            
            plot_data.append({
                'season': season,
                'answer': answer,
                'rank': rank,
                'count': count,
                'hover_text': hover_text
            })
    
    legend_order = [answer for answer, count in appearance_counts.most_common()]
    
    return pd.DataFrame(plot_data), legend_order

def plot_bump_chart(df, legend_order, top_n=20):
    """
    Creates and saves a prettier bump chart visualization for answer ranks.
    """
    fig = px.line(
        df,
        x='season',
        y='rank',
        color='answer',
        markers=True,
        custom_data=['hover_text'],
        category_orders={'answer': legend_order},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        title='Changing Ranks of Top 20 Answers by Season',
        labels={'season': 'Season', 'rank': 'Rank', 'answer': 'Answer'},
        line_shape='spline',
        render_mode='svg'
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(
            autorange=False,          # MODIFIED: Explicitly disable autoranging
            range=[top_n + 0.5, 0.5], # This [max, min] order forces the reversal
            fixedrange=True,
            tickvals=list(range(1, top_n + 1)),
            title='Rank',
            gridcolor='lightgrey'
        ),
        xaxis=dict(
            title='Season',
            gridcolor='lightgrey'
        ),
        legend_title_text='Top Answers',
        font=dict(family="Arial, sans-serif")
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=6, line=dict(width=1, color='Black')),
        connectgaps=False,
        hovertemplate="%{customdata}<extra></extra>"
    )

    fig.write_html("charts/jeopardy_answer_rank_bump_chart.html")
    print("Bump chart saved to charts/jeopardy_answer_rank_bump_chart.html")


if __name__ == '__main__':
    data_path = 'data'
    
    print("Analyzing answer frequencies across all seasons...")
    season_counts = analyze_answer_frequencies(data_path)
    
    print("Processing answer ranks for the Top 20...")
    ranks_df, legend_order = process_ranks(season_counts, top_n=20)
    
    ranks_df = ranks_df.sort_values(by=['answer', 'season'])
    
    if not ranks_df.empty:
        print("Generating bump chart...")
        plot_bump_chart(ranks_df, legend_order, top_n=20)
    else:
        print("No data available to plot.")