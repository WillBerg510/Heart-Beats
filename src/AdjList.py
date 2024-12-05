import TrackNode as Node
import random
from Similarity import determine_similarity

class AdjList:
    def __init__(self): # Create empty adjacency list
        self.list = {}
        self.last_played = []

    def get_list(self): # Return adjacency list
        return self.list

    def add_node(self, node: Node.TrackNode): # Add song to the adjacency list with no connections
        if (node.get_name(), node.get_artist()) not in self.list:
            # Each node is a dictionary with a tuple(name, artist) as the key and a list[node object, [neighbors], [weights]] as the values
            self.list[(node.get_name(), node.get_artist())] = [node ,[], []]

    def get_adjacent(self, node: Node.TrackNode): # Get neighbors of a song that could be played after the song
        if (node.get_name(), node.get_artist()) in self.list:
            return self.list[(node.get_name(), node.get_artist())][1]

    def get_similarity_scores(self, node: Node.TrackNode): # Get similarity scores of a song to its neighbors
        if (node.get_name(), node.get_artist()) in self.list:
            return self.list[(node.get_name(), node.get_artist())][2]

    def get_starting_song(self): # Determine starting point for the graph by picking a random song
        all_nodes = []
        for value in self.list.values():
            all_nodes.append(value[0])
        return all_nodes[random.randint(0, len(all_nodes) - 1)]
    
    def get_next_song(self, node: Node.TrackNode, bpm): # Get the next song to be queued
        value = self.list[(node.get_name(), node.get_artist())]
        closest_distance = 1000
        closest_node = 0
        for next_node in value[1]: # Go through each neighbor to find the one that has the closest BPM to the heart rate
            if abs(next_node.get_bpm() - bpm) < closest_distance and not next_node in self.last_played:
                closest_node = next_node
                closest_distance = abs(next_node.get_bpm() - bpm)
        self.last_played.append(closest_node) # Add a song to the last 5 played so that it won't be played again for a while
        if len(self.last_played) > 5:
            self.last_played.pop(0)
        return closest_node

    def form_connections(self): # Connect nodes together by finding the most similar songs to each node
        all_nodes = []
        for value in self.list.values(): # Get list of all nodes
            all_nodes.append(value[0])
        for node1 in all_nodes:
            most_similar_nodes = []
            highest_similarities = []
            for node2 in all_nodes:
                if node1 != node2:
                    similarity = determine_similarity(node1, node2) # Get similarity scores of every pair of songs

                    if len(highest_similarities) < 10: # Only hold the top 10 most similar songs
                        most_similar_nodes.append(node2)
                        highest_similarities.append(similarity)
                    elif similarity > min(highest_similarities):
                        index = highest_similarities.index(min(highest_similarities))
                        most_similar_nodes[index] = node2
                        highest_similarities[index] = similarity
            
            self.list[(node1.get_name(), node1.get_artist())][1] = most_similar_nodes # Add edges into the adjacency list
            self.list[(node1.get_name(), node1.get_artist())][2] = highest_similarities # Add weights into the adjacency list