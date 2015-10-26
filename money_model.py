import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

class Money_Agent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id):
        self.unique_id = unique_id
        self.wealth = 1

    def step(self, model):
        self.move(model)
        if self.wealth > 0:
            self.give_money(model)

    def move(self, model):
        """Take a random step."""
        grid = model.grid
        possible_steps = grid.get_neighborhood(
            self.pos, moore=True, include_center=True)
        choice = random.choice(possible_steps)
        grid.move_agent(self, choice)

    def give_money(self, model):
        grid = model.grid
        pos = [self.pos]
        others = grid.get_cell_list_contents(pos)
        if len(others) > 1:
            other = random.choice(others)
            other.wealth += 1
            self.wealth -= 1


class Money_Model(Model):
    def __init__(self, N, width=50, height=50, torus=True):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, torus)
        self.create_agents()
        self.dc = DataCollector({"Gini": lambda m: m.compute_gini()},
                               {"Wealth": lambda a: a.wealth})
        self.running = True

    def create_agents(self):
        for i in range(self.num_agents):
            a = Money_Agent(i)
            self.schedule.add(a)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.dc.collect(self)
        self.schedule.step()
        
    def run_model(self, steps):
        for i in range(steps):
            self.step()
    
    def compute_gini(self):
        agent_wealths = [agent.wealth for agent in self.schedule.agents]
        x = sorted(agent_wealths)
        N = self.num_agents
        B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
        return (1 + (1/N) - 2*B)
