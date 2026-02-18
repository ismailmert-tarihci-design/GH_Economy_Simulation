"""
Pack processing system for the Bluestar Economy Simulator.

Handles pack opening mechanics:
- Deterministic vs Monte Carlo pack count selection
- Card types table lookups with floor matching
- CardPull tracking for daily simulation
"""

from dataclasses import dataclass
from random import Random
from typing import Optional

import numpy as np

from simulation.models import CardTypesRange, GameState, SimConfig


@dataclass
class CardPull:
    """Represents a single card pull from a pack."""

    pack_name: str
    pull_index: int


def _get_card_types_for_count(
    card_types_table: dict[int, CardTypesRange], total_unlocked: int
) -> CardTypesRange:
    """
    Look up card types range for a given total unlocked count using floor matching.

    Returns the CardTypesRange (min/max) for the highest threshold ≤ total_unlocked.
    If total_unlocked is below all thresholds, returns the range for the lowest threshold.
    """
    matching_keys = [k for k in card_types_table.keys() if int(k) <= total_unlocked]
    if not matching_keys:
        # Below all thresholds — fall back to the lowest tier
        best_key = min(card_types_table.keys())
    else:
        best_key = max(matching_keys)
    return card_types_table[best_key]


def process_packs_for_day(
    game_state: GameState,
    config: SimConfig,
    rng: Optional[Random] = None,
    day_pack_counts: Optional[dict[str, float]] = None,
) -> list[CardPull]:
    """
    Process pack openings for a single day.

    For each pack type in config:
    - Compute number of packs to open (deterministic or MC)
    - Look up card types for current total_unlocked
    - Generate CardPull objects for each card

    Args:
        game_state: Current game state (contains current card collection)
        config: Simulation configuration with pack definitions
        rng: Random instance for MC mode (None = deterministic)
        day_pack_counts: Pack counts for this day. Falls back to
            day 0 of daily_pack_schedule if not provided.

    Returns:
        List of CardPull objects for the day
    """
    pulls: list[CardPull] = []
    total_unlocked = len(game_state.cards)

    if day_pack_counts is None:
        day_pack_counts = (
            config.daily_pack_schedule[0] if config.daily_pack_schedule else {}
        )

    for pack_config in config.packs:
        pack_name = pack_config.name

        daily_avg = day_pack_counts.get(pack_name, 0.0)

        # Determine number of packs to open
        if rng is None:
            num_packs = round(daily_avg)
        else:
            # MC: Poisson sampling seeded from the passed RNG for reproducibility
            poisson_seed = rng.randint(0, 2**31 - 1)
            local_gen = np.random.Generator(np.random.PCG64(poisson_seed))
            num_packs = int(local_gen.poisson(daily_avg))

        # Generate pulls for each pack
        for pack_index in range(num_packs):
            # Look up card types range for current unlocked count
            card_types_range = _get_card_types_for_count(
                pack_config.card_types_table,
                total_unlocked,
            )

            # Deterministic: round midpoint; MC: random int in [min, max]
            if rng is None:
                card_types = round((card_types_range.min + card_types_range.max) / 2)
            else:
                card_types = rng.randint(card_types_range.min, card_types_range.max)

            # Create CardPull for each card type
            for card_index in range(card_types):
                pull = CardPull(
                    pack_name=pack_name,
                    pull_index=len(pulls),
                )
                pulls.append(pull)

    return pulls
