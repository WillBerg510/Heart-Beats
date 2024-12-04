def determine_similarity(node1, node2): # Return a similarity score of two songs/track nodes
  similarity = 0 # Maximum similarity score will be 1000

  if node1.get_artist() == node2.get_artist(): # Artist match is worth 50 points
      similarity += 50

  if node1.get_genres() == [] or node2.get_genres() == []: # If genres can't be compared, add 40 points
      similarity += 40
  else: # If genres can be compared, up to 100 points are valued for exact genre matches and an additional 100 points are valued for word matches in genres
      shared_genres = 0
      shared_genre_words = set()
      for genre in node1.get_genres():
          if genre in node2.get_genres():
              shared_genres += 1
          for word in genre.split(' '):
              for other_genre in node2.get_genres():
                  if other_genre.find(word) != -1:
                      shared_genre_words.add(word)
      if shared_genres == 1:
          similarity += 60
      elif shared_genres == 2:
          similarity += 80
      elif shared_genres > 2:
          similarity += 100
      if len(shared_genre_words) == 1:
          similarity += 60
      elif len(shared_genre_words) == 2:
          similarity += 80
      elif len(shared_genre_words) > 2:
          similarity += 100
  
  words1 = node1.get_name().split(' ')
  words2 = node2.get_name().split(' ')
  shared_words = 0
  for word in words1:
      if word in words2:
          shared_words += 1
  similarity += min(shared_words * 20, 150) # Up to 150 points are valued for word matches in song names

  name1 = node1.get_name()
  name2 = node2.get_name()

  if name1[0].lower() == name2[0].lower():
    similarity += 50 # If the songs have the same first character, 50 points are added

  shared_letters = 0
  for char in name1:
      index = name2.lower().find(char.lower())
      if index != -1:
          shared_letters += 1
          name2 = name2[:index] + name2[index + 1:]
  similarity += int((shared_letters / max(len(name1), len(node2.get_name()))) * 450) # Up to 450 points are valued for letter matches in song names

  similarity += max((10 - abs(int(node1.get_release_year()) - int(node2.get_release_year()))), 0) * 10 # Up to 100 points for how close the release years are

  return similarity