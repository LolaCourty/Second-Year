from dijkstar import Graph, find_path

ttl = 3
obstacles = []


def add_obstacle(pos_obstacle, pos_robot, pos_dest):
    # Create graph
    graph = Graph(undirected=True)
    for j in range(5):
        for i in range(8):
            graph.add_edge((i, 2*j), (i+1, 2*j), 1)
            graph.add_edge((2*j, i), (2*j, i+1), 1)

    global obstacles
    new_list = []
    # Add new obstacle
    new_list.append([pos_obstacle, ttl])
    # Compute obstacles to keep
    for i in range(len(obstacles)):
        if obstacles[i][1] != 0:
            new_list.append([obstacles[i][0], obstacles[i][1]-1])
    obstacles = new_list

    # Delete nodes from graph
    for obstacle in obstacles:
        graph.remove_node(obstacle[0])

    path = find_path(graph, pos_robot, pos_dest)
    return path.nodes

def initial_path(pos_robot, pos_dest):
    # Create graph
    graph = Graph(undirected=True)
    for j in range(5):
        for i in range(8):
            graph.add_edge((i, 2*j), (i+1, 2*j), 1)
            graph.add_edge((2*j, i), (2*j, i+1), 1)

    path = find_path(graph, pos_robot, pos_dest)
    return path.nodes


if __name__ == "__main__":
    print(initial_path((0,0),(5,6)))
    print(add_obstacle((2,0),(1,0),(8,8)))
