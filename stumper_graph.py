import os
import json
from collections import defaultdict
import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pyvis.network import Network
import logging

# --- Configuration ---
CONFIG = {
    "BASE_DATA_PATH": "data/",
    "MODEL_NAME": 'all-MiniLM-L6-v2',
    "TOP_N_EDGES": 3,
    "SIMILARITY_THRESHOLD": 0.45,
    "MIN_TOTAL_STUMPERS": 25,
    "OUTPUT_HTML_FILE": "charts/jeopardy_stumper_similarity_graph.html",
    "CACHE_PATH": "cache"
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

def aggregate_category_data(game_files):
    """
    Aggregates appearances, stumper counts/text, and total clue counts for each category.
    """
    stumper_texts = defaultdict(str)
    category_counts = defaultdict(int)
    total_stumper_counts = defaultdict(int)
    stumper_clues = defaultdict(list)
    category_clue_counts = defaultdict(int)
    
    logging.info(f"Processing {len(game_files)} game files...")
    for file_path in game_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for round_data in data.get("rounds", []):
                for category in round_data.get("categories", []):
                    name = category.get("name")
                    clues = category.get("clues", [])
                    
                    if not name or not clues or "potpourri" in name.lower():
                        continue
                    
                    category_counts[name] += 1
                    category_clue_counts[name] += len(clues)
                    
                    for clue in clues:
                        if "Triple Stumper" in clue.get("wrong_contestants", []):
                            total_stumper_counts[name] += 1
                            stumper_texts[name] += f' {clue.get("clue", "")} {clue.get("answer", "")}'
                            stumper_clues[name].append({
                                "clue": clue.get("clue", "N/A"),
                                "answer": clue.get("answer", "N/A")
                            })

        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Skipping malformed file {file_path}: {e}")
            continue
            
    return stumper_texts, category_counts, total_stumper_counts, stumper_clues, category_clue_counts

def get_embeddings(texts_dict):
    """Encodes texts into vector embeddings using a sentence-transformer model."""
    model = SentenceTransformer(CONFIG['MODEL_NAME'])
    corpus = list(texts_dict.values())
    logging.info(f"Encoding {len(corpus)} documents...")
    return model.encode(corpus, show_progress_bar=True)

def build_graph(similarity_matrix, category_names, category_counts, total_stumper_counts, stumper_clues, category_clue_counts):
    """Builds a NetworkX graph with rescaled node sizes for better visual distinction."""
    G = nx.Graph()

    # --- MODIFIED: Pre-calculate ratios to find min/max for scaling ---
    ratios = {}
    for name in category_names:
        total_stumpers = total_stumper_counts.get(name, 0)
        total_clues = category_clue_counts.get(name, 1)
        ratios[name] = total_stumpers / total_clues if total_clues > 0 else 0

    min_ratio = min(ratios.values()) if ratios else 0
    max_ratio = max(ratios.values()) if ratios else 0
    
    # Define the output visual size range
    min_size = 10
    max_size = 50
    
    for name in category_names:
        total_appearances = category_counts.get(name, 0)
        total_stumpers = total_stumper_counts.get(name, 0)
        stumper_ratio = ratios.get(name, 0)
        
        # --- MODIFIED: Rescale the node size for better visual contrast ---
        if max_ratio > min_ratio:
            normalized_ratio = (stumper_ratio - min_ratio) / (max_ratio - min_ratio)
        else:
            normalized_ratio = 0.5 # Default to medium size if all ratios are the same
        
        node_size = float(min_size + normalized_ratio * (max_size - min_size))
        
        clue_list_preview = stumper_clues.get(name, [])[:5]
        clue_answer_strings = [f"- {item['clue']}: {item['answer']}" for item in clue_list_preview]
        stumpers_preview_text = "\n".join(clue_answer_strings)

        title = (
            f"{name}\n"
            f"Category Appeared {total_appearances} time(s)\n"
            f"Total Triple Stumpers: {total_stumpers}\n"
            f"Triple Stumper Ratio: {stumper_ratio:.1%}\n"
            f"-----------------------------\n"
            f"{stumpers_preview_text}"
        )
        G.add_node(name, size=node_size, title=title)

    logging.info("Building graph edges from similarity matrix...")
    for i in range(len(category_names)):
        sim_scores = similarity_matrix[i]
        sorted_indices = np.argsort(sim_scores)[::-1]
        edges_added = 0
        for j in sorted_indices[1:]:
            if edges_added >= CONFIG['TOP_N_EDGES']:
                break
            score = float(sim_scores[j])
            if score >= CONFIG['SIMILARITY_THRESHOLD']:
                cat_i, cat_j = category_names[i], category_names[j]
                G.add_edge(cat_i, cat_j, weight=score, title=f"{score:.2f}", value=score)
                edges_added += 1
                
    return G

def main():
    """Main function to run the full pipeline."""
    cache_dir = CONFIG['CACHE_PATH']
    cache_prefix = f"stumper_ratio_{CONFIG['MIN_TOTAL_STUMPERS']}_"
    vectors_cache_file = os.path.join(cache_dir, f"{cache_prefix}vectors.npy")
    names_cache_file = os.path.join(cache_dir, f"{cache_prefix}names.json")
    all_stumper_texts_cache = os.path.join(cache_dir, "all_stumper_texts_v6.json")
    all_counts_cache = os.path.join(cache_dir, "all_category_counts_v6.json")
    all_total_stumpers_cache = os.path.join(cache_dir, "all_total_stumpers_v6.json")
    all_stumper_clues_cache = os.path.join(cache_dir, "all_stumper_clues_v6.json")
    all_clue_counts_cache = os.path.join(cache_dir, "all_clue_counts_v6.json")
    
    os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(vectors_cache_file) and os.path.exists(names_cache_file):
        logging.info("Loading filtered data from cache...")
        category_vectors = np.load(vectors_cache_file)
        with open(names_cache_file, 'r') as f: category_names = json.load(f)
        with open(all_counts_cache, 'r') as f: category_counts = json.load(f)
        with open(all_total_stumpers_cache, 'r') as f: total_stumper_counts = json.load(f)
        with open(all_stumper_clues_cache, 'r') as f: stumper_clues = json.load(f)
        with open(all_clue_counts_cache, 'r') as f: category_clue_counts = json.load(f)
    else:
        logging.info("Cache not found for current settings. Starting full data processing.")
        game_files = get_all_game_files(CONFIG['BASE_DATA_PATH'])
        stumper_texts, category_counts, total_stumper_counts, stumper_clues, category_clue_counts = aggregate_category_data(game_files)

        with open(all_stumper_texts_cache, 'w') as f: json.dump(stumper_texts, f)
        with open(all_counts_cache, 'w') as f: json.dump(category_counts, f)
        with open(all_total_stumpers_cache, 'w') as f: json.dump(total_stumper_counts, f)
        with open(all_stumper_clues_cache, 'w') as f: json.dump(stumper_clues, f)
        with open(all_clue_counts_cache, 'w') as f: json.dump(category_clue_counts, f)
        
        logging.info(f"Original unique category count: {len(category_counts)}")

        filtered_names = {
            name for name, count in total_stumper_counts.items() 
            if count >= CONFIG["MIN_TOTAL_STUMPERS"]
        }
        filtered_stumper_texts = { name: text for name, text in stumper_texts.items() if name in filtered_names }
        
        logging.info(f"Filtered count (>{CONFIG['MIN_TOTAL_STUMPERS']} total Triple Stumpers): {len(filtered_names)}")
        
        category_names = list(filtered_stumper_texts.keys())
        category_vectors = get_embeddings(filtered_stumper_texts)
        
        logging.info(f"Saving filtered data to cache in '{cache_dir}'...")
        np.save(vectors_cache_file, category_vectors)
        with open(names_cache_file, 'w') as f: json.dump(category_names, f)

    logging.info("Calculating similarity matrix...")
    similarity_matrix = cosine_similarity(category_vectors)
    
    G = build_graph(similarity_matrix, category_names, category_counts, total_stumper_counts, stumper_clues, category_clue_counts)

    logging.info("Coloring graph components...")
    components = nx.connected_components(G)
    colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFA1", "#FFC300", "#C70039", "#900C3F", "#581845"]
    for i, component in enumerate(components):
        color = colors[i % len(colors)]
        for node in component:
            G.nodes[node]['color'] = color
    
    logging.info(f"Generating interactive graph: {CONFIG['OUTPUT_HTML_FILE']}")
    net = Network(height="90vh", width="100%", cdn_resources='remote', bgcolor="white", font_color="black")
    net.from_nx(G)
    options = """
    const options = {
      "physics": {
        "enabled": true,
        "forceAtlas2Based": {
          "gravitationalConstant": -250,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08,
          "damping": 0.4,
          "avoidOverlap": 0
        },
        "solver": "forceAtlas2Based",
        "stabilization": { "iterations": 200 }
      },
      "layout": { "improvedLayout": false }
    }
    """
    net.set_options(options)
    net.save_graph(CONFIG['OUTPUT_HTML_FILE'])
    
    logging.info(f"Success! Open '{CONFIG['OUTPUT_HTML_FILE']}' in your browser to view the graph.")

if __name__ == "__main__":
    main()