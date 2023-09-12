import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from tqdm import tqdm
from normalizing_flows.bijections.base import Bijection
from normalizing_flows.utils import flatten_event, get_batch_shape


class Flow(nn.Module):
    def __init__(self, bijection: Bijection):
        super().__init__()
        self.register_module('bijection', bijection)
        self.register_buffer('loc', torch.zeros(self.bijection.n_dim))
        self.register_buffer('covariance_matrix', torch.eye(self.bijection.n_dim))

    @property
    def base(self):
        return torch.distributions.MultivariateNormal(loc=self.loc, covariance_matrix=self.covariance_matrix)

    def base_log_prob(self, z):
        zf = flatten_event(z, self.bijection.event_shape)
        log_prob = self.base.log_prob(zf)
        return log_prob

    def log_prob(self, x: torch.Tensor, context: torch.Tensor = None):
        if context is not None:
            assert context.shape[0] == x.shape[0]
            context = context.to(self.loc)
        z, log_det = self.bijection.forward(x.to(self.loc), context=context)
        log_base = self.base_log_prob(z)
        return log_base + log_det

    def sample(self, n: int, context: torch.Tensor = None, no_grad: bool = False, return_log_prob: bool = False):
        """
        If context given, sample n vectors for each context vector.
        Otherwise, sample n vectors.

        :param n:
        :param context:
        :param no_grad:
        :return:
        """
        if context is not None:
            z = self.base.sample(sample_shape=torch.Size((n, len(context))))
            context = context[None].repeat(*[n, *([1] * len(context.shape))])  # Make context shape match z shape
            assert z.shape[:2] == context.shape[:2]
        else:
            z = self.base.sample(sample_shape=torch.Size((n,)))
        if no_grad:
            z = z.detach()
            with torch.no_grad():
                x, log_det = self.bijection.inverse(z, context=context)
        else:
            x, log_det = self.bijection.inverse(z, context=context)
        x = x.to(self.loc)

        if return_log_prob:
            log_prob = self.base_log_prob(z) + log_det
            return x, log_prob
        return x

    def fit(self,
            x_train: torch.Tensor,
            n_epochs: int = 500,
            lr: float = 0.05,
            batch_size: int = 1024,
            shuffle: bool = True,
            show_progress: bool = False,
            w_train: torch.Tensor = None):
        """

        :param x_train:
        :param n_epochs:
        :param lr: learning rate. In general, lower learning rates are recommended for high-parametric bijections.
        :param batch_size:
        :param shuffle:
        :param show_progress:
        :param w_train: training data weights
        :return:
        """
        if w_train is None:
            batch_shape = get_batch_shape(x_train, self.bijection.event_shape)
            w_train = torch.ones(batch_shape)
        if batch_size is None:
            batch_size = len(x_train)
        optimizer = torch.optim.AdamW(self.parameters(), lr=lr)
        dataset = TensorDataset(x_train, w_train)
        data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

        n_event_dims = int(torch.prod(torch.as_tensor(self.bijection.event_shape)))

        if show_progress:
            iterator = tqdm(range(n_epochs), desc='Fitting NF')
        else:
            iterator = range(n_epochs)

        for _ in iterator:
            for batch_x, batch_w in data_loader:
                optimizer.zero_grad()

                log_prob = self.log_prob(batch_x.to(self.loc))
                w = batch_w.to(self.loc)
                assert log_prob.shape == w.shape
                loss = -torch.mean(log_prob * w) / n_event_dims
                loss.backward()
                optimizer.step()

                if show_progress:
                    iterator.set_postfix_str(f'Loss: {loss:.4f}')

    def variational_fit(self,
                        target,
                        n_epochs: int = 10,
                        lr: float = 0.01,
                        n_samples: int = 1000):
        # target must have a .sample method that takes as input the batch shape
        optimizer = torch.optim.AdamW(self.parameters(), lr=lr)
        for i in range(n_epochs):
            x_train = target.sample((n_samples,)).to(self.loc.device)
            optimizer.zero_grad()
            loss = -self.log_prob(x_train).mean()
            loss.backward()
            optimizer.step()
