import TrackNode as Node

class AdjList:
    def __init__(self):
        self.list = {}

    def get_list(self):
        return self.list

    def add_node(self, node: Node.TrackNode):
        if (node.get_name(), node.get_artist()) not in self.list:
            self.list[(node.get_name(), node.get_artist())] = [node ,[], []]

    def get_adjacent(self, node: Node.TrackNode):
        if (node.get_name(), node.get_artist()) in self.list:
            return self.list[(node.get_name(), node.get_artist())][1]

    def get_similarity_scores(self, node: Node.TrackNode):
        if (node.get_name(), node.get_artist()) in self.list:
            return self.list[(node.get_name(), node.get_artist())][2]

    def form_connections(self): # Connect nodes together by finding the most similar songs to each node
        all_nodes = []
        for value in self.list.values():
            all_nodes.append(value[0])
        for node1 in all_nodes:
            most_similar_nodes = []
            highest_similarities = []
            for node2 in all_nodes:
                if node1 != node2:
                    similarity = 0 # Maximum similarity score will be 1000

                    if node1.get_artist() == node2.get_artist(): # Artist match is worth 100 points
                        similarity += 100

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
                    shared_letters = 0
                    for char in name1:
                        index = name2.find(char)
                        if index != -1:
                            shared_letters += 1
                            name2 = name2[:index] + name2[index + 1:]
                    similarity += int((shared_letters / max(len(name1), len(node2.get_name()))) * 450) # Up to 450 points are valued for letter matches in song names

                    similarity += max((10 - abs(int(node1.get_release_year()) - int(node2.get_release_year()))), 0) * 10 # Up to 100 points for how close the release years are

                    if len(highest_similarities) < 8:
                        most_similar_nodes.append(node2)
                        highest_similarities.append(similarity)
                    elif similarity > min(highest_similarities):
                        index = highest_similarities.index(min(highest_similarities))
                        most_similar_nodes[index] = node2
                        highest_similarities[index] = similarity
            
            self.list[(node1.get_name(), node1.get_artist())][1] = most_similar_nodes
            self.list[(node1.get_name(), node1.get_artist())][2] = highest_similarities