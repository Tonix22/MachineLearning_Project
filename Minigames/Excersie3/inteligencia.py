import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class XORNET(nn.Module):
    def __init__(self, lr, n_actions):
        super(XORNET,self).__init__()

        self.fc1 = nn.Linear(2, 2)
        self.fc2 = nn.Linear(2, 1)

        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss   = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')

        self.to(self.device)

    def forward(self,state):
        layer1  = T.Sigmoid(self.fc1(state))
        actions = self.fc2(layer1)
        return actions

class nnq():
    def __init__(self, n_actions, lr, gamma=0.80, epsilon=.1, eps_dec=1e-5, eps_min=0.01):
        self.lr=lr
        self.n_actions = n_actions
        self.gamma   = gamma
        self.epsilon = epsilon
        self.eps_dec = eps_dec
        self.eps_min = eps_min
        self.action_space = [i for i in range(self.n_actions)]
        self.Q = XORNET(self.lr,self.n_actions)

    def choose_action(self, observations):   
        if np.random.rand() > self.epsilon:
            state   = T.tensor(observations, dtype=T.float).to(self.Q.device) 
            action = self.Q.forward(state)
        else:
            action = np.random.choice(self.action_space)
        return action

    def decrement_epsilon(self):
        self.epsilon = self. epsilon - self.eps_dec if self.epsilon > self.eps_min else self.eps_min
        
    def learn(self, state,action, reward,state_):
        self.Q.optimizer.zero_grad()
        states = T.tensor(state,dtype=T.float).to(self.Q.device)
        actions = T.tensor(action).to(self.Q.device)
        rewards = T.tensor(reward).to(self.Q.device)
        states_ = T.tensor(state_, dtype=T.float).to(self.Q.device)
        q_pred = self.Q.forward(states)[actions]
        q_next = self.Q.forward(states_).max()
        q_target = reward + self.gamma*q_next
        loss = self.Q.loss(q_target, q_pred).to(self.Q.device)
        loss.backward()
        self.Q.optimizer.step()
        self.decrement_epsilon()