from langgraph.graph import StateGraph, MessageState, START, END

class State(MessageState):
    pass

def plan(state: MessageState):
    pass

def retrieve(state: MessageState):
    pass

def reason(state: MessageState):
    pass

def write(state: MessageState):
    pass

graph = StateGraph(MessageState)

# Declare nodes
graph.add_node(plan)
graph.add_node(retrieve)
graph.add_node(reason)
graph.add_node(write)

# Create edges
graph.add_edge(START, 'plan')
graph.add_edge('plan', 'retrieve')
graph.add_edge('retrieve', 'reason')
graph.add_edge('reason', 'write')
graph.add_edge('write', END)