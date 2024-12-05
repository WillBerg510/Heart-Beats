import TrackNode as Node
import random
from Similarity import determine_similarity

class Map:
  def __init__(self):
    # This map is implemented with a hash table: each item is a pair of a key and a value
    # In this case, each key is a tempo range and each value is an array of songs/track nodes
    self.table = []
    self.table.append([(0, 9), []])
    self.table.append([(10, 19), []])
    self.table.append([(20, 29), []])
    self.table.append([(30, 39), []])
    self.table.append([(40, 49), []])
    self.table.append([(50, 59), []])
    self.table.append([(60, 69), []])
    self.table.append([(70, 79), []])
    self.table.append([(80, 89), []])
    self.table.append([(90, 99), []])
    self.table.append([(100, 109), []])
    self.table.append([(110, 119), []])
    self.table.append([(120, 129), []])
    self.table.append([(130, 139), []])
    self.table.append([(140, 149), []])
    self.table.append([(150, 159), []])
    self.table.append([(160, 169), []])
    self.table.append([(170, 179), []])
    self.table.append([(180, 189), []])
    self.table.append([(190, 199), []])
    self.table.append([(200, 209), []])
    self.table.append([(200, 209), []])
    self.table.append([(210, 219), []])
    self.table.append([(220, 229), []])
    self.table.append([(230, 239), []])
    self.table.append([(240, 249), []])
    self.table.append([(250, 259), []])
    self.table.append([(260, 269), []])
    self.table.append([(270, 279), []])
    self.table.append([(280, 289), []])
    self.table.append([(290, 299), []])
    self.last_played = []

  def get_nodes(self, key):
    for pair in self.table:
      if pair[0] == key:
        return pair[1]
    return -1

  def add_node(self, key, node):
    for pair in self.table:
      if pair[0] == key:
        pair[1].append(node)

  def get_map(self):
    return self.table

  def get_starting_song(self, bpm):
    songs = []
    while len(songs) == 0:
      songs = self.get_nodes((int(bpm / 10) * 10, int(bpm / 10) * 10 + 9))
      bpm += 10
      if bpm > 300:
        bpm = 0
    starting_song = songs[random.randint(0, len(songs) - 1)]
    self.last_played.append(starting_song)
    return starting_song

  def get_next_song(self, node, bpm):
    result = 0
    while not result:
      songs = self.get_nodes((int(bpm / 10) * 10, int(bpm / 10) * 10 + 9))
      best_similarity = 0
      best_node = 0
      for next_node in songs:
        if not next_node == node:
          similarity = determine_similarity(node, next_node)
          if similarity > best_similarity and not next_node in self.last_played:
            best_node = next_node
            best_similarity = similarity
      result = best_node
      bpm += 10
      if bpm > 300:
        bpm = 0
    self.last_played.append(result)
    if len(self.last_played) > 4:
      self.last_played.pop(0)
    return result