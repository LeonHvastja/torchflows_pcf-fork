import pytest
import torch

from src.bijections.finite.autoregressive.layers import AffineForwardMaskedAutoregressive


@pytest.mark.parametrize('n_dim', [2, 3])
@torch.no_grad()
def test_linear_made_layer(n_dim):
    torch.manual_seed(0)
    x = torch.randn(5, n_dim)
    layer = AffineForwardMaskedAutoregressive(n_dim, n_layers=1)
    z, log_det_forward = layer.forward(x)
    w, log_det_inverse = layer.inverse(z)

    max_error = float((x - w).max().abs())
    assert torch.allclose(x, w), f"{max_error = }"
