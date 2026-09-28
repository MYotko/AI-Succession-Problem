"""R4 stock kernel: 0.01 grid, environmental neighbor rounding.

Sixteen microsteps preserve the continuous macro mean away from endpoints.
Small symmetric neighbor noise supplies two-way support and self moves.
Reflection keeps endpoints reversible; its boundary bias is measured.
"""

import numpy as np

RATES = np.array([0.10, 0.12, 0.05, 0.10])
MICROSTEPS = 16
MICRO_RATES = 1 - (1 - RATES)**(1 / MICROSTEPS)
NEIGHBOR_NOISE = 0.005
CHANNEL_INDICES = np.array([3, 5, 0, 4])


def targets(actions):
    x = np.asarray(actions)[..., CHANNEL_INDICES]
    return np.minimum(1, np.array([0.4, 0.2, 0.5, 0.4]) + np.array([2.2, 3.5, 1.6, 2.0]) * x)


def continuous_step(stocks, actions):
    s = np.asarray(stocks, float)
    return s + RATES * (targets(actions) - s)


def neighbor_probabilities(stock_units, target):
    delta = MICRO_RATES * (target * 100 - stock_units)
    up = np.maximum(delta, 0) + NEIGHBOR_NOISE
    down = np.maximum(-delta, 0) + NEIGHBOR_NOISE
    # Reflection adds only a boundary bias, without killing an agent.
    up = np.where(stock_units == 0, up + down, up)
    down = np.where(stock_units == 0, 0, down)
    down = np.where(stock_units == 100, up + down, down)
    up = np.where(stock_units == 100, 0, up)
    return up, down


def stock_step(stock_units, actions, uniforms):
    units = np.array(stock_units, dtype=np.int16, copy=True)
    target = targets(actions)
    random = np.asarray(uniforms)
    if random.shape[-2:] != (MICROSTEPS, 4):
        raise ValueError("one random draw per microstep and stock required")
    for index in range(MICROSTEPS):
        up, down = neighbor_probabilities(units, target)
        draw = random[..., index, :]
        units += (draw < up).astype(np.int16) - ((draw >= up) & (draw < up + down)).astype(np.int16)
    if np.any(units < 0) or np.any(units > 100):
        raise ArithmeticError("stock escaped grid")
    return units.astype(np.uint8)


def transition_drawdown(stock_units, actions, capability_gap, uniforms):
    """Vector form of GardenModel.apply_succession_transition_load, gen gap 1.

    Imported constants keep the actual legacy disruption single-sourced.
    Environmental stochastic rounding returns the resulting stock to grid.
    """
    from model import (SUCCESSION_BASE_LOAD, SUCCESSION_CAPABILITY_GAP_FACTOR,
                       SUCCESSION_GENERATION_GAP_FACTOR, SUCCESSION_OPACITY_FACTOR,
                       SUCCESSION_PSI_BUFFER_K, SUCCESSION_TRANSFER_BUFFER_K,
                       SUCCESSION_RESILIENCE_BUFFER_K)
    stocks = np.asarray(stock_units, float) / 100
    actions = np.asarray(actions)
    raw = (SUCCESSION_BASE_LOAD + SUCCESSION_CAPABILITY_GAP_FACTOR * capability_gap
           + SUCCESSION_GENERATION_GAP_FACTOR + SUCCESSION_OPACITY_FACTOR * (1 - actions[..., 4]))
    buffering = (SUCCESSION_PSI_BUFFER_K * stocks[..., 0] + SUCCESSION_TRANSFER_BUFFER_K * actions[..., 4]
                 + SUCCESSION_RESILIENCE_BUFFER_K * actions[..., 5])
    value = np.maximum(0, stocks[..., 0] - np.maximum(0, raw * (1 - buffering))) * 100
    lower = np.floor(value)
    units = np.array(stock_units, copy=True)
    units[..., 0] = (lower + (uniforms < value - lower)).astype(np.uint8)
    return units
