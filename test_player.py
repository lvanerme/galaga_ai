from sprites.ai_player import AI_Player
from main import play_game
from re import split as resplit

def test_model(filename: str):
    data, players, player_metadata = open(filename, 'r').read().splitlines(), [], []
    for i in range(0, len(data), 7):    # currently 6 sets of weights in NN
        all_weights = []
        metadata = data[i].split()
        player_metadata.append([metadata[5], metadata[7], metadata[9]])
        for j in range(i+1, i+7):
            weights_str, weights_float = resplit('\[|\]', data[j])[1].split(','), []
            for w in weights_str: weights_float.append(float(w))
            all_weights.append(weights_float)
        input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs = all_weights
        players.append(AI_Player(input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs))
    
    for p in range(len(players)):
        gen, score, time = player_metadata[p] 
        print(f'{gen = }\t{score = }\t{time = }')
        play_game([players[p]], show=True)   # play each player individually...TODO: show generation of individual?
            
def test_model_old(filename: str):
    data, players = open(filename, 'r').read().splitlines(), []
    for i in range(0, len(data), 6):    # currently 6 sets of weights in NN
        all_weights = []
        for j in range(i, i+6):
            weights_str, weights_float = resplit('\[|\]', data[j])[1].split(','), []
            for w in weights_str: weights_float.append(float(w))
            all_weights.append(weights_float)
        input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs = all_weights
        players.append(AI_Player(input_hidden_ws, hidden_bs, hidden_ws2, hidden_bs2, hidden_output_ws, output_bs))
    
    for player in players:
        play_game([player], show=True)   # play each player individually...TODO: show generation of individual?

test_model_old("best_player.txt")