import torch
from torch import nn


class HarvestNet(nn.Sequential):
    def __init__(self,in_channel,out_channel):
        layers=[
            nn.Linear(in_channel,16),
            nn.LeakyReLU(),
            nn.Linear(16,out_channel)
        ]
        super(HarvestNet,self).__init__(*layers)
        self.apply(weight_init)

def weight_init(real_model):
    if isinstance(real_model,nn.Linear):
        nn.init.normal_(real_model.weight,0,0.1)
        if real_model.bias is not None:
            nn.init.constant_(real_model.bias,0)

    