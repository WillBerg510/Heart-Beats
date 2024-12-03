import TrackNode as Node

class AdjList:
    def __init__(self):
        self.list = {}

    def get_list(self):
        return self.list

    def add_node(self, node: Node.TrackNode):
        if node.get_name() not in self.list:
            self.list[node.get_name()] = [node ,[]]