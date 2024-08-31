import requests
import csv
def onSale():
    # Define the base URL for the CheapShark API
    base_url = "https://www.cheapshark.com/api/1.0/deals"
 

    # Parameters to get deals from Steam sorted by historical low price
    params = {
        "storeID": "1",  # Steam's store ID in CheapShark
        "sortBy": "price",  # Sort by price to get the lowest prices first
        "metacritic": "80" , # Filter games with Metacritic score greater than 80
        "isOnSale": "1", # Filter games that are currently on sale
    }

    # Make the API request
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response to JSON
        deals = response.json()
      


        # Output the game names and prices
        outputlist=[]
        for deal in deals:
            if(deal['salePrice'] != deal['normalPrice']):
                outputlist.append({
                    deal["steamAppID"]: f"{deal['title']}, currently rated **{deal['metacriticScore']}** on Metacritic, is {deal['salePrice']} (was {deal['normalPrice']})"
                })
        return outputlist
    else:
        print("Failed to retrieve data from CheapShark API")
        return []





def csv_games():
    # Read the game IDs from the CSV file
    game_ids = []
    with open('custom_games.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            game_ids.append(row[0])

    # Function to chunk the game_ids list
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    # Define the base URL for the CheapShark API games endpoint
    base_url = "https://www.cheapshark.com/api/1.0/games"

    

    # Process game IDs in chunks of 25
    for chunk in chunker(game_ids, 25):
        # Convert the chunk list to a comma-separated string for the API request
        ids_param = ','.join(chunk)

        # Make the API request for a chunk of game IDs
        response = requests.get(base_url, params={"ids": ids_param, "format": "array"})

        # Create a list to store the game details
        outputlist = []
       # Assuming 'response' is a variable holding the response from a request made earlier
        if response.status_code == 200:
            games = response.json()
            outputlist = []

            for game in games:
                salePrice = None
                retailPrice = None

                # Iterate through each deal for the current game
                for deal in game.get('deals', []):
                    if deal.get('storeID') == "1" and float(deal.get('price')) != float(deal.get('retailPrice')):
                        salePrice = deal.get('price')
                        retailPrice = deal.get('retailPrice')
                        break  # Exit the loop once the correct deal is found

                # Only add to outputlist if a deal meeting the criteria was found
                if salePrice and retailPrice:
                    game_info = game.get('info', {})
                    steamAppID = game_info.get('steamAppID')
                    title = game_info.get('title')
                    outputlist.append({
                        steamAppID: f"{title}, is $ {salePrice} (was ${retailPrice})"
                    })

        else:
            print(f"Failed to retrieve data for game IDs: {','.join(chunk)}")  # Assuming 'chunk' is defined elsewhere

        return outputlist



def steam_to_cheapshark(steam_game_id):
    # Endpoint that presumably accepts a Steam game ID and returns game details
    api_url = "https://www.cheapshark.com/api/1.0/games"
    params = {"steamAppID": steam_game_id}
    response = None  # Pre-initialize response
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            game_data = response.json()
            # Assuming the response contains a list of games, and we're interested in the first one
            if game_data and isinstance(game_data, list) and len(game_data) > 0:
                # Extracting the CheapShark game ID from the first game in the list
                cheapshark_game_id = game_data[0].get('gameID')
                return cheapshark_game_id
            else:
                print("Game not found or invalid response format.")
                return steam_game_id
        else:
            print(f"Failed to retrieve game details. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None

def search(steamid):
    # Define the base URL for the CheapShark API
    base_url = "https://www.cheapshark.com/api/1.0/games"

    # Make the API request
    response = requests.get(base_url, params={"steamAppID": steamid})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response to JSON
        games = response.json()

        # Output the game names and prices
        outputlist = []
        for game in games:
            outputlist.append({
                game["steamAppID"]: f"{game['external']} is $ {game['cheapest']}"
            })
        return outputlist
    else:
        print("Failed to retrieve data from CheapShark API")
        return []