"""Small CNN for 5-class white-blood-cell image research.

About 1 million trainable weights. Built for a laptop GPU (or CPU fallback).
Research risk classification - not for clinical use.
"""

from __future__ import annotations

import torch
from torch import nn


class SmallWbcCnn(nn.Module):
    """Five conv blocks + global average pool + linear head (~1M weights)."""

    def __init__(self, n_classes: int = 5) -> None:
        super().__init__()
        self.features = nn.Sequential(
            _conv_block(3, 32),
            _conv_block(32, 64),
            _conv_block(64, 128),
            _conv_block(128, 256),
            _conv_block(256, 256),
        )
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(256, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x))


def _conv_block(in_ch: int, out_ch: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
        nn.BatchNorm2d(out_ch),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2),
    )


def count_trainable_parameters(model: nn.Module) -> int:
    """Count weights the optimizer will update."""
    return sum(param.numel() for param in model.parameters() if param.requires_grad)
