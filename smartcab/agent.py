import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from random import randint
import numpy as np
class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.deadline=0
        self.counter=0;
        self.Qtable={} #creating a 2d Q table.
        self.gamma=0
        self.alpha=0;
        self.options=['forward', 'left', 'right',None]
        for i in ['green', 'red']:  #lights
          for j in [None, 'forward', 'left', 'right']:#oncoming
              for k in [None, 'forward', 'left', 'right']:#valid options
                for l in ['forward', 'left', 'right']:  ## possible next_waypoints
                    self.Qtable[(i,j,k,l)] = [0.0] *4  # Q table, initialised every element to 0.


        self.timer=1.0;#increases everytime a cab makes a move. 
        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        if self.deadline!=0:
            self.counter+=1
        self.reward=0
        self.action=None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        self.deadline = self.env.get_deadline(self)
        action=None;
        # TODO: Update state
        self.state = (inputs['light'],inputs['oncoming'],inputs['left'], self.next_waypoint)
        # TODO: Select action according to your policy
        #action = random.choice(self.env.valid_actions) # Executes a random action and gets a reward
        epsilon=1/(self.timer*10);
        c=list()
        #about once in 200 times, the below algorithm chooses a random action, so that i can explore options he have never tried before,
        #which would hopefully help it discover better options that it has missed while learning.
        if(random.random()>=epsilon):
            for i in self.Qtable[self.state]:
                if i==max(self.Qtable[self.state]):
                    c.append(i)
        else:
            for i in self.Qtable[self.state]:
                c.append(i)
        action = random.choice(c)    
        Qmax=self.Qtable[self.state].index(action);#chooses the action based on the highest value for that state in the Q table\\
                                                   #Makes a random choice if there are many actions with the same highest value for Q\
        action = self.options[Qmax]
        reward = self.env.act(self, action)
        new_waypoint = self.planner.next_waypoint()
        new_state = (inputs['light'],inputs['oncoming'],inputs['left'],new_waypoint)
        self.gamma=1
        self.timer+=1
        self.alpha=1/(self.timer)
        #TODO: Learn policy based on state, action, reward
        self.Qtable[self.state][self.options.index(action)] = (1-self.alpha)*self.Qtable[self.state][self.options.index(action)] +(self.alpha * (reward + self.gamma * max(self.Qtable[new_state])))
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(self.deadline, inputs, action, reward)  # [debug]
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    if a.deadline!=0:
        a.counter+=1
    print "The smartcab reached its destination {}% of the times".format(a.counter)
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

if __name__ == '__main__':
    run()
