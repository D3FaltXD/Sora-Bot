import requests


#For Input Validation

def is_valid_game_id(game_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        # The response is a JSON object with the game_id as a key
        # If the game exists, the 'success' key will be True
        game_data = response.json()
        if game_data[str(game_id)]['success']:
            return True
        return False
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False  # Optionally, return False or handle differently if the request fails

