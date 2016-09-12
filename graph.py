class WeightedGraph:
    '''A graph has a set of vertices and a set of edges, with each
    edge being an ordered pair of vertices. '''

    def __init__ (self):
        self._alist = {}

    def add_vertex (self, vertex):
        ''' Adds 'vertex' to the graph
        Preconditions: None
        Postconditions: self.is_vertex(vertex) -> True
        '''
        if vertex not in self._alist:
            self._alist[vertex] = dict()
            self._alist[vertex]['neighbours'] = dict()
            self._alist[vertex]['ownership'] = 0
            self._alist[vertex]['armies'] = 0

    def add_edge (self, source, destination, weight):
        ''' Adds the edge (source, destination)
        Preconditions: 
        self.is_vertex(source) -> True,
        self.is_vertex(destination) -> True,
        Postconditions:
        self.is_edge(source, destination) -> True
        '''
        self._alist[source]['neighbours'][destination] = weight
    
    def get_weight (self, source, destination):
        '''Returns the weight associated with this edge.
        Precondition: self.is_edge(source, destination) -> True'''
        return self._alist[source]['neighbours'][destination]

    def is_edge (self, source, destination):
        '''Checks whether (source, destination) is an edge
        '''
        return (self.is_vertex(source)
                and destination in self._alist[source]['neighbours'])

    def is_vertex (self, vertex):
        '''Checks whether vertex is in the graph.
        '''
        return vertex in self._alist

    def neighbours (self, vertex):
        '''Returns the set of neighbours of vertex. DO NOT MUTATE
        THIS SET.
        Precondition: self.is_vertex(vertex) -> True
        '''
        return self._alist[vertex]['neighbours'].keys()
    
    def neighbours_and_weights (self, vertex):
        return self._alist[vertex]['neighbours'].items()

    def vertices (self):
        '''Returns a set-like container of the vertices of this
        graph.'''
        return self._alist.keys()
    
    def owner (self, vertex):
        '''Returns the owner of the vertex
        Precondition: self.is_vertex(vertex -> True
        '''
        return self._alist[vertex]['ownership']
        
    def set_owner (self, vertex, player):
        '''Sets the ownership of the specified vertex to player'''
        self._alist[vertex]['ownership'] = player
    
    def armies (self, vertex):
        '''Returns the number of armies in the vertex'''
        return self._alist[vertex]['armies']
    
    def add_army (self, vertex, num):
        '''Adds the specified number of armies to the specified vertex
           Returns the resulting number of armies on that vertex'''
        self._alist[vertex]['armies'] += num
        return self._alist[vertex]['armies']
    
    def remove_army (self, vertex, num):
        '''Removes the specified number of armies to the specified vertex
           Returns the resulting number of armies on that vertex
                   (0 if less than 0)
        '''
        self._alist[vertex]['armies'] -= num
        if self._alist[vertex]['armies'] < 0:
            self._alist[vertex]['armies'] = 0
        return self._alist[vertex]['armies']

class WeightedUndirectedGraph (WeightedGraph):
    '''An undirected graph has edges that are unordered pairs of
    vertices; in other words, an edge from A to B is the same as one
    from B to A.'''

    def add_edge (self, a, b, w):
        '''We implement this as a directed graph where every edge has its
        opposite also added to the graph'''
        super().add_edge (a, b, w)
        super().add_edge (b, a, w)

