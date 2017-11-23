import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter
from torch.autograd import Variable

def init_hidden(batch_size, n_layers, n_hidden, d_type):
    if self.rnn_type == 'LSTM':
        return (Variable(d_type(n_layers, batch_size, n_hidden).zero_()),
                Variable(d_type(n_layers, batch_size, n_hidden).zero_()))
    else:
        return Variable(d_type(n_layers, batch_size, n_hidden).zero_())




class RNNModel(nn.Module):
    """Container module with a recurrent module, and a projection layer."""

    def __init__(self, rnn_type, n_input, n_hidden, n_projection, n_layers, dropout=0.5):
        super(RNNModel, self).__init__()
        self.rnn = getattr(nn, rnn_type)(n_input, n_hidden, n_layers, dropout=dropout, batch_first=True)
        self.proj = nn.Linear(n_hidden, n_projection)
        self.n_hidden = n_hidden
        self.n_projection = n_projection
        self.n_input = n_input
        self.n_layers = n_layers
        self.rnn_type = rnn_type


    def forward(self, input, hidden):
        output, hidden = self.rnn(input, hidden)
        output_prj = self.proj(output.view(output.size(0)*output.size(1), output.size(2)))
        return output_prj.view(output.size(0), output.size(1), output_prj.size(1)), hidden

    def init_hidden(self, batch_size, d_type):
        if self.rnn_type == 'LSTM':
            return (Variable(d_type(batch_size, self.n_layers, self.n_hidden).zero_()),
                    Variable(d_type(batch_size, self.n_layers, self.n_hidden).zero_()))
        else:
            return Variable(d_type(batch_size, self.n_layers, self.n_hidden).zero_())


class DepthwiseGatedConv1d(nn.Module):
    def __init__(self, in_channels, k_out_channels, kernel_size, stride=1, padding=0, dilatation=1, bias=True, activation_fn=nn.ELU):
        """
        Compute a depthwise gated convolution.
        Apply a different filter to every input channel
        :param in_channels: input channels
        :param k_out_channels: how many filters to apply to each feature
        :param kernel_size:  filter size in time
        :param stride: strides
        :param padding: zero padding
        :param dilatation: dilatation to apply
        :param bias: use bias or batch_norm
        :param activation_fn: activation function to use
        """
        super(DepthwiseGatedConv1d, self).__init__()
        out_channels = k_out_channels * in_channels

        self.conv_gate = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size,
                      groups=in_channels,
                      stride=stride,
                      padding=padding,
                      dilation=dilatation,
                      bias=True),
            nn.Sigmoid()
        )

        if bias:
            self.conv_filter = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size,
                          groups=in_channels,
                          stride=stride,
                          padding=padding,
                          dilation=dilatation,
                          bias=True),
                activation_fn()
            )
        else:
            self.conv_filter = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size,
                          stride=stride,
                          padding=padding,
                          dilation=dilatation,
                          bias=False),
                nn.BatchNorm1d(out_channels),
                activation_fn()
            )

    def forward(self, input):
        T = self.conv_gate(input)
        H = self.conv_filter(input)
        return torch.mul(H, T)
