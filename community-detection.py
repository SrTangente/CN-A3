import os
from collections import defaultdict
from clu_utils import *
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import networkx.algorithms.community as community
from net_drawing import network_plot_3D
from sklearn.metrics import jaccard_score, normalized_mutual_info_score
import igraph

def get_label_partition(net):
    label_com_generator = community.label_propagation_communities(net)
    #print('Label mod: ' + str(community.modularity(net, label_com_generator)))
    partition = {}
    try:
        next_label_com = label_com_generator.__next__()
        i = 0
        while next_label_com:
            for v in next_label_com:
                partition[v] = i
            i = i + 1
            next_label_com = label_com_generator.__next__()
    except StopIteration:
        return partition

def random_walk(net):
    g = igraph.Graph.Adjacency((nx.to_numpy_matrix(net) > 0).tolist())
    res = g.community_walktrap(steps=4)
    values = res.as_clustering().membership
    keys = list(net._adj.keys())
    #print('Random walk mod: '+str(g.modularity(values)))
    return dict(zip(keys,values))

def get_modularity_partitions(net):
    partition = {}
    mod_com = community.greedy_modularity_communities(net)
    #print('Greedy mod: '+str(community.modularity(net, mod_com)))
    for i in range(len(mod_com)):
        com = list(mod_com[i])
        for v in com:
            partition[v] = i
    return partition


def partition_to_clu(partition: dict):
    clu = []
    for v in partition.values():
        clu.append([])
    for k in partition.keys():
        clu[partition[k]].append(k)
    return clu

def clu_to_partition(clu):
    dict = {}
    for i in range(len(clu)):
        for k in clu[i]:
            dict[k] = i
    return dict


def parse_pajek_clu(lines):
    if isinstance(lines, str):
        lines = iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])

    labels = []  # in the order of the file, needed for matrix
    while lines:
        try:
            l = next(lines)
        except:  # EOF
            break
        if l.lower().startswith("*vertices"):
            l, nnodes = l.split()
            communities = defaultdict(list)
            for vertice in range(int(nnodes)):
                l = next(lines)
                community = int(l)
                communities.setdefault(community, []).append(vertice)
        else:
            break

    return [v for k, v in dict(communities).items()]


folders = ['toy', 'model', 'real']

for f in folders:
    graphs = os.listdir(f)
    for g in sorted(graphs, reverse=True):
        path = './' + f + '/' + g
        if (path.endswith("net")):
            net = nx.Graph(nx.read_pajek(path))
            coordinates = None
            print('GRAPH: '+path.split('/')[-1])
            #extract coordinates
            file = open(path, 'r')
            lines = file.read().split('\n')
            if len(lines[1].split(' ')) > 3:
                coordinates = {}
                for l in lines[1:]:
                    if l.__contains__('*Edges'):
                        break
                    splitted_line = l.split()
                    index = int(splitted_line[0])
                    name = splitted_line[1].replace('"', '')
                    cs = [float(c) for c in splitted_line[2:]]
                    coord = (cs[0], cs[1])
                    coordinates[name] = coord

            #generate community partitions
            mod_partition = get_modularity_partitions(net)
            label_partition = get_label_partition(net)
            random_walk_partition = random_walk(net)
            fig, axes = plt.subplots(1, 4)
            fig.set_size_inches(18.5, 10.5)
            axes[3].set_title('Reference partition')
            axes[3].invert_yaxis()

            try:
                clu = read_pajek_communities(path.replace('net', 'clu'))
                clu_partition = clu_to_partition(clu)
            except FileNotFoundError:
                clu = None
                fig, axes = plt.subplots(1, 3)

            axes[0].set_title('Modularity partition')
            axes[1].set_title('Label partition')
            axes[2].set_title('Random walk partition')
            axes[0].invert_yaxis()
            axes[1].invert_yaxis()
            axes[2].invert_yaxis()
            if coordinates is not None:
                nx.set_node_attributes(net, coordinates, 'coord')
                nx.draw(net, pos=coordinates, node_color=list(mod_partition.values()), ax=axes[0], node_size=100)
                nx.draw(net, pos=coordinates, node_color=list(label_partition.values()), ax=axes[1], node_size=100)
                nx.draw(net, pos=coordinates, node_color=list(random_walk_partition.values()), ax=axes[2], node_size=100)
                if clu is not None:
                    nx.draw(net, pos=coordinates, node_color=list(clu_partition.values()), ax=axes[3], node_size=100)
            else:
                nx.draw_kamada_kawai(net, node_color=list(mod_partition.values()), ax=axes[0], node_size=100)
                nx.draw_kamada_kawai(net, node_color=list(label_partition.values()), ax=axes[1], node_size=100)
                nx.draw_kamada_kawai(net, node_color=list(random_walk_partition.values()), ax=axes[2], node_size=100)
                if clu is not None:
                    nx.draw_kamada_kawai(net, node_color=list(clu_partition.values()), ax=axes[3], node_size=100)
            plt.show()
            fig.savefig('./images/'+path.split('/')[-1][:-4]+'.png',dpi=100)
            write_pajek_communities(partition_to_clu(mod_partition), path[:-4] + '_modularity.clu')
            write_pajek_communities(partition_to_clu(label_partition), path[:-4] + '_label.clu')
            write_pajek_communities(partition_to_clu(random_walk_partition), path[:-4] + '_randam_walk.clu')