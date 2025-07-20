import requests
from bs4 import BeautifulSoup
import os
import json
import re

BASE_URL = "https://j-archive.com/"

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'lxml')

def get_season_links(soup):
    links = []
    for link in soup.select('a[href^="showseason.php"]'):
        season_url = BASE_URL + link['href']
        if season_url not in links:
            links.append(season_url)
    return links

def get_game_links(soup):
    links = []
    for link in soup.select('a[href^="showgame.php"]'):
        game_url = BASE_URL + link['href']
        if game_url not in links:
            links.append(game_url)
    return links


def scrape_game(url):
    print(f"Scraping game: {url}")
    game_soup = get_soup(url)
    game_data = {"url": url, "rounds": []}

    rounds = ["jeopardy_round", "double_jeopardy_round", "final_jeopardy_round"]
    for round_name in rounds:
        round_table = game_soup.find('div', id=round_name)
        if not round_table:
            continue

        round_data = {"name": round_name, "categories": []}
        categories = round_table.find_all('td', class_='category_name')
        clues = round_table.find_all('td', class_='clue')

        for i, category in enumerate(categories):
            category_data = {"name": category.get_text(strip=True), "clues": []}
            start_index = i
            # This logic assumes a fixed 6x5 grid for the first two rounds
            if round_name != "final_jeopardy_round":
                for j in range(5):
                    clue_index = start_index + (j * len(categories))
                    if clue_index < len(clues):
                        clue_cell = clues[clue_index]
                        clue_text_element = clue_cell.find('td', class_='clue_text')
                        if not clue_text_element:
                            continue
                        clue_text = clue_text_element.get_text(strip=True)
                        
                        value_element = clue_cell.find(class_=['clue_value', 'clue_value_daily_double'])
                        value = value_element.get_text(strip=True) if value_element else ""

                        answer_html = ""
                        right_contestants = []
                        wrong_contestants = []

                        clue_id = clue_text_element.get('id')
                        if clue_id:
                            answer_element_id = clue_id + "_r"
                            answer_element = game_soup.find('td', id=answer_element_id)
                            if answer_element:
                                correct_response_element = answer_element.find('em', class_='correct_response')
                                if correct_response_element:
                                    answer_html = correct_response_element.get_text(strip=True)
                                
                                for contestant in answer_element.find_all('td', class_='right'):
                                    right_contestants.append(contestant.get_text(strip=True))
                                for contestant in answer_element.find_all('td', class_='wrong'):
                                    wrong_contestants.append(contestant.get_text(strip=True))
                        
                        category_data["clues"].append({
                            "clue": clue_text, 
                            "answer": answer_html,
                            "value": value,
                            "right_contestants": right_contestants,
                            "wrong_contestants": wrong_contestants
                        })
            else: # Final Jeopardy
                 clue_text_element = round_table.find('td', class_='clue_text')
                 clue_text = clue_text_element.get_text(strip=True) if clue_text_element else ""
                 answer_element = round_table.find('em', class_='correct_response')
                 answer_html = answer_element.get_text(strip=True) if answer_element else ""
                 category_data["clues"].append({"clue": clue_text, "answer": answer_html})


            round_data["categories"].append(category_data)
        game_data["rounds"].append(round_data)
    return game_data


def main():
    print("Starting scraper...")
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    main_soup = get_soup(BASE_URL)
    season_links = get_season_links(main_soup)
    print(f"Found {len(season_links)} season links.")

    # For testing, only process the first season and first game
    for season_link in season_links:
        season_number = season_link.split('=')[-1]
        season_dir = os.path.join(data_dir, season_number)
        if not os.path.exists(season_dir):
            os.makedirs(season_dir)
        
        print(f"Processing season: {season_link}")
        season_soup = get_soup(season_link)
        game_links = get_game_links(season_soup)
        print(f"Found {len(game_links)} games in season.")
        for game_link in game_links:
            game_id = game_link.split('=')[-1]
            file_path = os.path.join(season_dir, f"{game_id}.json")
            
            game_data = scrape_game(game_link)
            with open(file_path, 'w') as f:
                json.dump(game_data, f, indent=4)
            print(f"Saved data to {file_path}")

    print("Scraping complete.")


if __name__ == "__main__":
    main()
