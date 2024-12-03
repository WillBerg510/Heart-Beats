import TrackNode as Node

class AdjList:
    def __init__(self):
        self.list = {}

    def get_list(self):
        return self.list

    def add_node(self, node: Node.TrackNode):
        if node.get_name() not in self.list:
            self.list[node.get_name()] = [node ,[], []]

    def get_adjacent(self, node: Node.TrackNode):
        if node.get_name() in self.list:
            return self.list[node.get_name()][1]

    def get_similarity_scores(self, node: Node.TrackNode):
        if node.get_name() in self.list:
            return self.list[node.get_name()][2]

    def form_connections(self): # Connect nodes together by finding the most similar songs to each node
        all_nodes = []
        for value in self.list.values():
            all_nodes.append(value[0])
        for i in range(0, len(all_nodes)):
            node1 = all_nodes[i]
            most_similar_nodes = []
            highest_similarities = []
            for n in range(i + 1, len(all_nodes)):
                node2 = all_nodes[n]
                similarity = 0 # Maximum similarity score will be 500

                if node1.get_artist() == node2.get_artist():
                    similarity += 100

                if node1.get_genres() == [] or node2.get_genres() == []:
                    similarity += 40
                else:
                    shared_genres = 0
                    for genre in node1.get_genres():
                        if genre in node2.get_genres():
                            shared_genres += 1
                    if shared_genres == 1:
                        similarity += 60
                    elif shared_genres == 2:
                        similarity += 80
                    elif shared_genres > 2:
                        similarity += 100
                
                words1 = node1.get_name().split(' ')
                words2 = node2.get_name().split(' ')
                shared_words = 0
                for word in words1:
                    if word in words2:
                        shared_words += 1
                similarity += min(shared_words * 20, 100) # Add 20 for every word in common up to five words in common

                name1 = node1.get_name()
                name2 = node2.get_name()
                shared_letters = 0
                for char in name1:
                    index = name2.find(char)
                    if index != -1:
                        shared_letters += 1
                        name2 = name2[:index] + name2[index + 1:]
                similarity += int((shared_letters / max(len(name1), len(name2))) * 200) # Add up to 200 based on the ratio of similar letters to the length of the longer name

                if len(highest_similarities) < 4:
                    most_similar_nodes.append(node2)
                    highest_similarities.append(similarity)
                elif similarity > min(highest_similarities):
                    index = highest_similarities.index(min(highest_similarities))
                    most_similar_nodes[index] = node2
                    highest_similarities[index] = similarity
            
            for j in range(0, len(most_similar_nodes)):
                similar_node = most_similar_nodes[j]
                similarity = highest_similarities[j]
                if not similar_node in self.list[node1.get_name()][1]:
                    self.list[node1.get_name()][1].append(similar_node)
                    self.list[node1.get_name()][2].append(similarity)
                    self.list[similar_node.get_name()][1].append(node1)
                    self.list[similar_node.get_name()][2].append(similarity)