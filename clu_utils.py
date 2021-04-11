import networkx as nx
from networkx.utils import open_file
from collections import defaultdict

def parse_pajek_communities(lines):
    """Parse Pajek format partition from string or iterable.
    Parameters
    ----------
    lines : string or iterable
       Data in Pajek partition format.
    Returns
    -------
    communities (list) – List of communities
    See Also
    --------
    read_pajek_partition()
    """
    if isinstance(lines, str):
        lines = iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])

    while lines:
        try:
            l = next(lines)
        except:  # EOF
            break
        if l.lower().startswith("*vertices"):
            l, nnodes = l.split()
            communities = defaultdict(list)
            for vertex in range(int(nnodes)):
                l = next(lines)
                community = int(l)
                communities.setdefault(community, []).append(vertex)
        else:
            break

    return [v for k,v in dict(communities).items()]

@open_file(0, mode='rb')
def read_pajek_communities(path, encoding='UTF-8'):

    lines = (line.decode(encoding) for line in path)
    return parse_pajek_communities(lines)

@open_file(1, mode='wb')
def write_pajek_communities(communities, path, encoding='UTF-8'):
    for line in generate_pajek_communities(communities):
        line += '\r\n'
        path.write(line.encode(encoding))

def generate_pajek_communities(communities):
    """Generate lines in Pajek communities format (.clu).
    Parameters
    ----------
    communities : list
       A communities list
    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """

    # We need a copy of the communities to use the strategy of removing vertices
    communities_list = [inner_list[:] for inner_list in communities]
    nnodes = sum([len(vertex) for vertex in communities])

    # Write first line
    yield f"*Vertices {nnodes}"

    # We do not assume that vertices:
    # - Starts with the number 1
    # - Are correlative
    # Therefore we will look for the minimum then pop it

    for n in range(0, nnodes):
        # We look for the minimum vertex number
        vertex = min([min(item) for item in communities_list if item])

        # We find the community this vertex belongs to
        community = next(i for i, v in enumerate(communities_list) if vertex in v)

        # We put the community number in the row corresponding to the vertex
        # We add 1 because Pajek communities starts with number 1
        yield f"{community + 1}"

        # We remove this vertex from the communities structure
        communities_list[community].remove(vertex)