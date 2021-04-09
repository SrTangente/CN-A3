import os
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import networkx.algorithms.community as community


def get_label_partition(net):
    label_com_generator = community.label_propagation_communities(net)
    partition = {}
    next_label_com = label_com_generator.__next__()
    i = 0
    while next_label_com:
        for v in next_label_com:
            partition[v] = i
        i = i+1
        next_label_com = label_com_generator.__next__()
    return partition

def get_modularity_partitions(net):
    partition = {}
    mod_com = community.greedy_modularity_communities(net)
    for i in range(len(mod_com)):
        com = list(mod_com[i])
        for v in com:
            node = int(v)
            partition[node] = i
    return partition


def community_layout(g, partition):
    """
    Compute the layout for a modular graph.


    Arguments:
    ----------
    g -- networkx.Graph or networkx.DiGraph instance
        graph to plot

    partition -- dict mapping int node -> int community
        graph partitions


    Returns:
    --------
    pos -- dict mapping int node -> (float x, float y)
        node positions

    """

    pos_communities = _position_communities(g, partition, scale=3.)

    pos_nodes = _position_nodes(g, partition, scale=1.)

    # combine positions
    pos = dict()
    for node in g.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]

    return pos

def _position_communities(g, partition, **kwargs):

    # create a weighted graph, in which each node corresponds to a community,
    # and each edge weight to the number of edges between communities
    between_community_edges = _find_between_community_edges(g, partition)

    communities = set(partition.values())
    hypergraph = nx.DiGraph()
    hypergraph.add_nodes_from(communities)
    for (ci, cj), edges in between_community_edges.items():
        hypergraph.add_edge(ci, cj, weight=len(edges))

    # find layout for communities
    pos_communities = nx.spring_layout(hypergraph, **kwargs)

    # set node positions to position of community
    pos = dict()
    for node, community in partition.items():
        pos[node] = pos_communities[community]

    return pos

def _find_between_community_edges(g, partition):

    edges = dict()

    for (ni, nj) in g.edges():
        ci = partition[ni]
        cj = partition[nj]

        if ci != cj:
            try:
                edges[(ci, cj)] += [(ni, nj)]
            except KeyError:
                edges[(ci, cj)] = [(ni, nj)]

    return edges

def _position_nodes(g, partition, **kwargs):
    """
    Positions nodes within communities.
    """

    communities = dict()
    for node, community in partition.items():
        try:
            communities[community] += [node]
        except KeyError:
            communities[community] = [node]

    pos = dict()
    for ci, nodes in communities.items():
        subgraph = g.subgraph(nodes)
        pos_subgraph = nx.spring_layout(subgraph, **kwargs)
        pos.update(pos_subgraph)

    return pos

folders = ['toy', 'real', 'model']

for f in folders:
    graphs = os.listdir(f)
    for g in graphs:
        path = './'+f+'/'+g
        if(path.endswith("net")):
            print(path)
            net = nx.Graph(nx.read_pajek(path))
            mod_partition = get_modularity_partitions(net)

            label_partition = get_label_partition(net)
            positions = {}
            coordinates = []
            '''try:
                print(net.nodes)
                node_list = list(net.nodes)
                coordinates = [(n[1], n[2]) for n in node_list]
                for i in range(0, len(net.nodes)):
                    v = node_list[i]
                    positions[v] = coordinates[i]
            except IndexError:
                coordinates = None'''
            if len(coordinates) > 0:
                nx.drawing.draw(net, positions)
            else:
                nx.draw_kamada_kawai(net)
            plt.show()
