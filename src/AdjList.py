import TrackNode as Node
from Similarity import determine_similarity

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
                    similarity = determine_similarity(node1, node2)

                    if len(highest_similarities) < 8:
                        most_similar_nodes.append(node2)
                        highest_similarities.append(similarity)
                    elif similarity > min(highest_similarities):
                        index = highest_similarities.index(min(highest_similarities))
                        most_similar_nodes[index] = node2
                        highest_similarities[index] = similarity
            
            self.list[(node1.get_name(), node1.get_artist())][1] = most_similar_nodes
            self.list[(node1.get_name(), node1.get_artist())][2] = highest_similarities