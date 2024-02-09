from typing import Tuple, List

from normalizing_flows.bijections.finite.autoregressive.layers import (
    ShiftCoupling,
    AffineCoupling,
    AffineForwardMaskedAutoregressive,
    AffineInverseMaskedAutoregressive,
    RQSCoupling,
    RQSForwardMaskedAutoregressive,
    RQSInverseMaskedAutoregressive,
    InverseAffineCoupling,
    DSCoupling,
    ElementwiseAffine,
    UMNNMaskedAutoregressive,
    LRSCoupling,
    LRSForwardMaskedAutoregressive,
    ElementwiseShift
)
from normalizing_flows.bijections.base import BijectiveComposition
from normalizing_flows.bijections.finite.linear import ReversePermutation


class NICE(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, edge_list: List[Tuple[int, int]] = None, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            if edge_list is None:
                bijections.append(ReversePermutation(event_shape=event_shape))
            bijections.append(ShiftCoupling(event_shape=event_shape, edge_list=edge_list))
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class RealNVP(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, edge_list: List[Tuple[int, int]] = None, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            if edge_list is None:
                bijections.append(ReversePermutation(event_shape=event_shape))
            bijections.append(AffineCoupling(event_shape=event_shape, edge_list=edge_list))
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class InverseRealNVP(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, edge_list: List[Tuple[int, int]] = None, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            if edge_list is None:
                bijections.append(ReversePermutation(event_shape=event_shape))
            bijections.append(InverseAffineCoupling(event_shape=event_shape, edge_list=edge_list))
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class MAF(BijectiveComposition):
    """
    Expressive bijection with slightly unstable inverse due to autoregressive formulation.
    """

    def __init__(self, event_shape, n_layers: int = 2, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            bijections.extend([
                ReversePermutation(event_shape=event_shape),
                AffineForwardMaskedAutoregressive(event_shape=event_shape)
            ])
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class IAF(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            bijections.extend([
                ReversePermutation(event_shape=event_shape),
                AffineInverseMaskedAutoregressive(event_shape=event_shape)
            ])
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class CouplingRQNSF(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, edge_list: List[Tuple[int, int]] = None, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            if edge_list is None:
                bijections.append(ReversePermutation(event_shape=event_shape))
            bijections.append(RQSCoupling(event_shape=event_shape, edge_list=edge_list))
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class MaskedAutoregressiveRQNSF(BijectiveComposition):
    """
    Expressive bijection with unstable inverse due to autoregressive formulation.
    """

    def __init__(self, event_shape, n_layers: int = 2, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            bijections.extend([
                ReversePermutation(event_shape=event_shape),
                RQSForwardMaskedAutoregressive(event_shape=event_shape)
            ])
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class CouplingLRS(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, edge_list: List[Tuple[int, int]] = None, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseShift(event_shape=event_shape)]
        for _ in range(n_layers):
            if edge_list is None:
                bijections.append(ReversePermutation(event_shape=event_shape))
            bijections.append(LRSCoupling(event_shape=event_shape, edge_list=edge_list))
        bijections.append(ElementwiseShift(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class MaskedAutoregressiveLRS(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseShift(event_shape=event_shape)]
        for _ in range(n_layers):
            bijections.extend([
                ReversePermutation(event_shape=event_shape),
                LRSForwardMaskedAutoregressive(event_shape=event_shape)
            ])
        bijections.append(ElementwiseShift(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class InverseAutoregressiveRQNSF(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            bijections.extend([
                ReversePermutation(event_shape=event_shape),
                RQSInverseMaskedAutoregressive(event_shape=event_shape)
            ])
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class CouplingDSF(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 2, edge_list: List[Tuple[int, int]] = None, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            if edge_list is None:
                bijections.append(ReversePermutation(event_shape=event_shape))
            bijections.append(DSCoupling(event_shape=event_shape, edge_list=edge_list))
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)


class UMNNMAF(BijectiveComposition):
    def __init__(self, event_shape, n_layers: int = 1, **kwargs):
        if isinstance(event_shape, int):
            event_shape = (event_shape,)
        bijections = [ElementwiseAffine(event_shape=event_shape)]
        for _ in range(n_layers):
            bijections.extend([
                ReversePermutation(event_shape=event_shape),
                UMNNMaskedAutoregressive(event_shape=event_shape)
            ])
        bijections.append(ElementwiseAffine(event_shape=event_shape))
        super().__init__(event_shape, bijections, **kwargs)
