from poker_game_runner.state import Observation
from poker_game_runner.utils import Range, HandType
import time
import random
import http.client
import urllib.request
import json

class AI:
  def __init__(self):
    self.headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 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'
    }

  def setup(self, players: int, index: int, hands):
      self.messages = [
        {
            "role": "system",
            "content":  f"""
        You are playing no limit Texas Hold'em poker with {players} other players and your player position is {index}
        A card is represented by a 2-character string. 1 char with the rank and 1 char with the suit.
        examples: 'As' (ace of spades), '6d' (six of diamonds), 'Tc' (ten of clubs)
        Your private cards are: {hands}
        You must output only a single integer.
        0 = fold
        1 = call/check
        x > 1 raise to x

        You will be provided every round with community cards, number of active players, pot size and other information.
        """
        }
      ]
      self.payload = {
        "model": "gpt-3.5-turbo",
        "messages": self.messages
      }

  def round(self, my_cards, cards, round, output) -> int:
    self.messages.append(    {
            "role": "user",
            "content":  f"""
        You must output only a single integer.
        0 = fold
        1 = call/check
        x > 1 raise to x
        Your cards: {my_cards}, Community cards: {cards}, round: {round}, Legal outputs: {output}
        """
      })
    self.payload = {
      "model": "gpt-3.5-turbo",
      "messages": self.messages
    }
    val = self.call1()

    self.messages.append(    {
            "role": "assistant",
            "content":  f"{val}"
      })
    self.payload = {
      "model": "gpt-3.5-turbo",
      "messages": self.messages
    }
    return val

  def call1(self) -> int:
        try:
            # Convert payload to JSON string
            payload_str = json.dumps(self.payload).encode('utf-8')

            # Create a request
            req = urllib.request.Request('https://api.openai.com/v1/chat/completions', data=payload_str, headers=self.headers)

            # Perform the request
            with urllib.request.urlopen(req) as response:
                data = response.read()
            response_dict = json.loads(data.decode('utf-8'))
            print("AAAAAAAA " + response_dict["choices"][-1]["message"]["content"])
            return int(response_dict["choices"][-1]["message"]["content"])

        except Exception as e:
            print(f"Error: {e}")

        return 1
  
class Bot:
  def __init__(self):
    self.AI = AI()

  def get_name(self):
      return "I don't know what I am doing"

  def act(self, obs: Observation):
    if obs.current_round == 0:
       self.AI.setup(obs.get_player_count(), obs.my_index, obs.my_hand)
    return self.AI.round(obs.my_hand, obs.board_cards, obs.current_round, obs.legal_actions)
