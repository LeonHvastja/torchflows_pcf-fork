Bijection objects
====================

All normalizing flow transformations are bijections.
The following classes define forward and inverse pass methods which all flow architectures inherit.

.. autoclass:: torchflows.bijections.base.Bijection
    :members: __init__, forward, inverse

.. autoclass:: torchflows.bijections.base.BijectiveComposition
    :members: __init__

.. autoclass:: torchflows.bijections.continuous.base.ContinuousBijection
    :members: __init__, forward, inverse

.. autoclass:: torchflows.bijections.finite.multiscale.base.MultiscaleBijection
    :members: __init__

Inverting a bijection
---------------------

Each bijection can be inverted with the `invert` function.

.. autofunction:: torchflows.bijections.base.invert