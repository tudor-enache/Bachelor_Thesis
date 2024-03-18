#!/usr/bin/local python3
import threading
import time
from math import inf

class Message:
    def __init__(self, destination, code, last, payload):
        self.destination = destination
        self.code = code
        self.last = last
        self.payload = payload
        
class LSP:
    def __init__(self, src, seq, links):
        self.src = src
        self.seq = seq
        self.links = links
        
def newer(lsp1, lsp2):
    return lsp1.seq > lsp2.seq

class Node:
    def __init__(self, name):
        self.name = name
        self.connections = {}
        self.inq = []
        self.seq = 0
        self.lsdb = {self.name: {'seq': 0, 'links': {}}}
        self.frwrd = {}
        
    def __repr__(self):
        return f"node {self.name}"
        
    def addl(self, nodes):
        for node in nodes:
            self.lsdb[self.name]['links'][node.name] = {'node': node, 'cost': 1}
            self.connections[node.name] = node
        
    def add(self, lsp):
        self.lsdb[lsp.src] = {'seq': lsp.seq, 'links': lsp.links}
        
    def send(self, msg, dst):
        self.connections[dst].inq.append(msg)
        if msg.code != 1:
            print(f"{self.name} sent to {dst}")
        
    def send_remote(self, dst):
        msg = Message(dst, 2, self.name, f"Message from {self.name} for {dst}")
        self.send(msg, self.frwrd[dst])
        
    def receive(self):
        while True:
            if len(self.inq) > 0:
                msg = self.inq.pop(0)
                if msg.code == 1:
                    lsp = msg.payload
                    l = msg.last
                    if lsp.src not in self.lsdb or newer(lsp, self.lsdb[lsp.src]):
                        self.add(lsp)
                        for node in self.connections:
                            if node != l:
                                new = Message(None, 1, self.name, lsp)
                                self.send(new, node)
                elif msg.code == 2:
                    dst = msg.destination
                    if dst == self.name:
                        print(f"{self.name} has received: {msg.payload}")
                    else:
                        self.send(Message(dst, 2, self.name, msg.payload), self.frwrd[dst])
                else:
                    print(msg.payload)
                    
    def flood(self):
        lsp = LSP(self.name, self.seq, self.lsdb[self.name]['links'])
        msg = Message(None, 1, self.name, lsp)
        for node in self.connections:
            self.send(msg, node)
            
    def calculate_frwrd_table(self):
        spt = dijkstra(self.name, self.lsdb)
        frwrd = {}
        for node in spt:
            if spt[node] == -1:
                continue
            elif spt[node] == self.name:
                frwrd[node] = node
            else:
                frwrd[node] = spt[node]
                while True:
                    if spt[frwrd[node]] == self.name:
                        break
                    else:
                        frwrd[node] = spt[frwrd[node]]
        self.frwrd = frwrd
        
class Client:
    pass

class Server:
    pass
          
def dijkstra(node, lsdb):
    graph = {}
    for src in lsdb:
        graph[src] = []
        for dst in lsdb[src]['links']:
            graph[src].append((dst, lsdb[src]['links'][dst]['cost']))
    
    unvisited = [i for i in range(len(graph))]
    distance = {}
    previous = {}
    for nnode in graph:
        distance[nnode] = inf
        previous[nnode] = -1
    distance[node] = 0
    curr = node
    
    while len(unvisited) > 0:
        for u, w in graph[curr]:
            if distance[curr] + w < distance[u] and u in unvisited:
                distance[u] = distance[curr] + w
                previous[u] = curr
    
        unvisited.remove(curr)
        
        min_len = inf
        for u in unvisited:
            if distance[u] < min_len:
                min = u
                min_len = distance[u]
        curr = min
        
    return previous
            
def test_flooding():
    node0 = Node(0)
    node1 = Node(1)
    node2 = Node(2)
    node0.addl([node1])
    node1.addl([node0, node2])
    node2.addl([node1])
    nodes = [node0, node1, node2]
    
    for node in nodes:
        rt = threading.Thread(target=node.receive)
        rt.start()
        
    for node in nodes:
        st = threading.Thread(target=node.flood)
        st.start()
        
    time.sleep(5)
        
    for node in nodes:
          print(f"Node{node.name} fowarding table: {node.calculate_frwrd_table()}")
    
def addc(nodes, src, conns):
    node_conns = []
    for conn in conns:
        node_conns.append(nodes[conn.name])
    
    nodes[src.name].addl(node_conns)
    for node in conns:
        node.addl([src])
        
def start(nodes):
    for node in nodes:
        rt = threading.Thread(target=node.receive)
        rt.start()
    for node in nodes:
        st = threading.Thread(target=node.flood)
        st.start()
    time.sleep(5)
    for node in nodes:
        node.calculate_frwrd_table()
        
def test_remote():
    nodes = []
    for i in range(8):
        nodes.append(Node(i))
    addc(nodes, nodes[0], [nodes[1], nodes[2]])
    addc(nodes, nodes[1], [nodes[3], nodes[4]])
    addc(nodes, nodes[2], [nodes[5]])
    addc(nodes, nodes[4], [nodes[6]])
    addc(nodes, nodes[5], [nodes[7]])
    
    start(nodes)
    
    nodes[0].send_remote(7)
test_remote()