import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np

dtype = torch.FloatTensor

nn_input_dim = 223
hly1_n = 300
hly2_n = 400
hly3_n = 300
hly4_n = 200
hly5_n = 100
hly6_n = 100
hly7_n = 100
# hly8_n = 100
nn_output_dim = 1

class Net(nn.Module):
    
    def __init__(self):
        super(Net, self).__init__()
        self.hl1 = nn.Linear(nn_input_dim, hly1_n)
        self.hl2 = nn.Linear(hly1_n, hly2_n)
        self.hl3 = nn.Linear(hly2_n, hly3_n)
        self.hl4 = nn.Linear(hly3_n, hly4_n)
        self.hl5 = nn.Linear(hly4_n, hly5_n)
        self.hl6 = nn.Linear(hly5_n, hly6_n)
        self.hl7 = nn.Linear(hly6_n, hly7_n)
#         self.hl8 = nn.Linear(hly7_n, hly8_n)        
        self.out = nn.Linear(hly7_n, nn_output_dim)
        
    def forward(self, x):
        x = F.leaky_relu(self.hl1(x))
        x = F.leaky_relu(self.hl2(x))
        x = F.leaky_relu(self.hl3(x))
        x = F.leaky_relu(self.hl4(x))
        x = F.leaky_relu(self.hl5(x))
        x = F.leaky_relu(self.hl6(x))        
        x = F.leaky_relu(self.hl7(x))        
#         x = F.leaky_relu(self.hl8(x))
        x = self.out(x)
        return x


    
def torch_version(df_inputs, net):
    input = Variable(torch.from_numpy(df_inputs.values)).type(dtype)
    return np.round(net(input).data.cpu().numpy(),5).ravel()    