from typing import Union, Tuple, List

import torch

from torchflows.bijections.finite.autoregressive.layers import ElementwiseAffine
from torchflows.bijections.base import Bijection, BijectiveComposition
from torchflows.utils import get_batch_shape, unflatten_event, flatten_event, flatten_batch, unflatten_batch


class ResidualBijection(Bijection):
    def __init__(self, event_shape: Union[torch.Size, Tuple[int, ...]]):
        """

        g maps from (*batch_shape, n_event_dims) to (*batch_shape, n_event_dims)

        :param event_shape:
        """
        super().__init__(event_shape)
        self.g: callable = None

    def log_det(self, x, **kwargs):
        raise NotImplementedError

    def forward(self,
                x: torch.Tensor,
                context: torch.Tensor = None,
                skip_log_det: bool = False) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_shape = get_batch_shape(x, self.event_shape)
        x_flat = flatten_batch(flatten_event(x, self.event_shape), batch_shape)
        g_flat = self.g(x_flat)
        g = unflatten_event(unflatten_batch(g_flat, batch_shape), self.event_shape)

        z = x + g

        if skip_log_det:
            log_det = torch.full(size=batch_shape, fill_value=torch.nan)
        else:
            x_flat = flatten_batch(flatten_event(x, self.event_shape).clone(), batch_shape)
            x_flat.requires_grad_(True)
            log_det = -unflatten_batch(self.log_det(x_flat, training=self.training), batch_shape)

        return z, log_det

    def inverse(self,
                z: torch.Tensor,
                context: torch.Tensor = None,
                skip_log_det: bool = False,
                n_iterations: int = 25) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_shape = get_batch_shape(z, self.event_shape)
        x = z
        for _ in range(n_iterations):
            x_flat = flatten_batch(flatten_event(x, self.event_shape), batch_shape)
            g_flat = self.g(x_flat)
            g = unflatten_event(unflatten_batch(g_flat, batch_shape), self.event_shape)

            x = z - g

        if skip_log_det:
            log_det = torch.full(size=batch_shape, fill_value=torch.nan)
        else:
            x_flat = flatten_batch(flatten_event(x, self.event_shape).clone(), batch_shape)
            x_flat.requires_grad_(True)
            log_det = -unflatten_batch(self.log_det(x_flat, training=self.training), batch_shape)

        return x, log_det


class ResidualComposition(BijectiveComposition):
    def __init__(self, blocks: List[ResidualBijection]):
        assert len(blocks) > 0
        event_shape = blocks[0].event_shape

        updated_layers = [ElementwiseAffine(event_shape)]
        for i in range(len(blocks)):
            updated_layers.append(blocks[i])
            updated_layers.append(ElementwiseAffine(event_shape))

        super().__init__(
            event_shape=updated_layers[0].event_shape,
            layers=updated_layers,
            context_shape=updated_layers[0].context_shape
        )
