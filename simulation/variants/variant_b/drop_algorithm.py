"""Drop algorithm for Variant B — Hero Card System.

Decides: shared card (Gold/Blue) or hero card?
For hero cards: bucket heroes by level -> pick bucket -> pick hero (anti-streak)
-> roll rarity -> pick card (lowest-level catch-up).
"""

from __future__ import annotations

import hashlib
from random import Random
from typing import Any, Dict, List, Optional, Tuple

from simulation.variants.variant_b.models import (
    HeroCardConfig,
    HeroCardGameState,
    HeroCardRarity,
    HeroCardState,
    HeroProgressState,
)
from simulation.variants.variant_b.hero_deck import get_unlocked_cards


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _weighted_choice(
    items: List[Any],
    weights: List[float],
    rng: Optional[Random] = None,
) -> Optional[Any]:
    """Pick one item via weighted random (RNG) or highest-weight (deterministic)."""
    if not items:
        return None
    total = sum(weights)
    if total <= 0:
        return None

    if rng:
        roll = rng.random() * total
        cumulative = 0.0
        for item, w in zip(items, weights):
            cumulative += w
            if roll <= cumulative:
                return item
        return items[-1]
    else:
        # Deterministic: pick highest weight
        best_idx = max(range(len(weights)), key=lambda i: weights[i])
        return items[best_idx]


# ---------------------------------------------------------------------------
# Hero vs Shared decision (unchanged logic)
# ---------------------------------------------------------------------------

def decide_hero_or_shared(
    game_state: HeroCardGameState,
    config: HeroCardConfig,
    rng: Optional[Random] = None,
) -> str:
    """Decide whether the next pull is a hero card or a shared card.

    Returns: "hero" or "shared"
    """
    dc = config.drop_config
    base_hero = dc.hero_vs_shared_base_rate

    # Pity system: guarantee hero card after N shared-only pulls
    if dc.pity_counter_threshold > 0 and game_state.pity_counter >= dc.pity_counter_threshold:
        return "hero"

    if rng:
        roll = rng.random()
    else:
        # Deterministic: hash-based
        h = hashlib.md5(f"hero_or_shared_{game_state.day}_{game_state.pity_counter}".encode())
        roll = int(h.hexdigest()[:8], 16) / 0xFFFFFFFF

    return "hero" if roll < base_hero else "shared"


# ---------------------------------------------------------------------------
# Hero card selection — bucket-based algorithm
# ---------------------------------------------------------------------------

def _build_hero_buckets(
    heroes: List[Tuple[str, HeroProgressState]],
) -> Tuple[List[Tuple[str, HeroProgressState]], List[Tuple[str, HeroProgressState]], List[Tuple[str, HeroProgressState]]]:
    """Divide heroes (sorted by level ascending) into bottom/middle/top buckets.

    Bucket size = floor(n/3). Remainder heroes go to the bottom bucket.
    """
    n = len(heroes)
    bucket_size = n // 3
    remainder = n % 3
    bottom_end = bucket_size + remainder
    middle_end = bottom_end + bucket_size

    bottom = heroes[:bottom_end]
    middle = heroes[bottom_end:middle_end]
    top = heroes[middle_end:]
    return bottom, middle, top


def select_hero_card(
    game_state: HeroCardGameState,
    config: HeroCardConfig,
    rng: Optional[Random] = None,
) -> Optional[Tuple[str, str]]:
    """Select which hero's card to drop using the bucket-based algorithm.

    Steps:
        1. Rank unlocked heroes by level, split into 3 buckets
        2. Roll which bucket (configurable weights, empty buckets redistribute)
        3. Pick hero from bucket (anti-streak decay on consecutive same-hero pulls)
        4. Roll rarity (configurable weights, only from rarities hero has unlocked cards for)
        5. Pick card of that rarity (lowest-level-first catch-up weighting)

    Returns: (hero_id, card_id) or None if no hero cards available.
    """
    dc = config.drop_config

    # Step 1: Collect heroes that have at least one unlocked card, sorted by level
    eligible_heroes: List[Tuple[str, HeroProgressState]] = []
    for hero_id, hero_state in game_state.heroes.items():
        if get_unlocked_cards(hero_state):
            eligible_heroes.append((hero_id, hero_state))

    if not eligible_heroes:
        return None

    eligible_heroes.sort(key=lambda x: x[1].level)

    # Step 2: Build buckets and select one
    bottom, middle, top = _build_hero_buckets(eligible_heroes)

    buckets = []
    bucket_weights = []
    for bucket, weight in [
        (bottom, dc.bucket_bottom_weight),
        (middle, dc.bucket_middle_weight),
        (top, dc.bucket_top_weight),
    ]:
        if bucket:  # Only include non-empty buckets
            buckets.append(bucket)
            bucket_weights.append(weight)

    if not buckets:
        return None

    chosen_bucket = _weighted_choice(buckets, bucket_weights, rng)
    if chosen_bucket is None:
        return None

    # Step 3: Pick hero from bucket with anti-streak decay
    hero_weights = []
    for hero_id, hero_state in chosen_bucket:
        w = 1.0
        if hero_id == game_state.last_hero_pulled and game_state.hero_streak_count > 0:
            w *= dc.streak_decay_hero ** game_state.hero_streak_count
        hero_weights.append(w)

    chosen_hero = _weighted_choice(chosen_bucket, hero_weights, rng)
    if chosen_hero is None:
        return None
    hero_id, hero_state = chosen_hero

    # Step 4: Roll rarity (only from rarities this hero has unlocked cards for)
    unlocked = get_unlocked_cards(hero_state)
    cards_by_rarity: Dict[HeroCardRarity, List[HeroCardState]] = {}
    for card in unlocked:
        cards_by_rarity.setdefault(card.rarity, []).append(card)

    rarity_config = [
        (HeroCardRarity.COMMON, dc.rarity_weight_common),
        (HeroCardRarity.RARE, dc.rarity_weight_rare),
        (HeroCardRarity.EPIC, dc.rarity_weight_epic),
    ]

    available_rarities = []
    available_rarity_weights = []
    for rarity, weight in rarity_config:
        if rarity in cards_by_rarity:
            available_rarities.append(rarity)
            available_rarity_weights.append(weight)

    if not available_rarities:
        return None

    chosen_rarity = _weighted_choice(available_rarities, available_rarity_weights, rng)
    if chosen_rarity is None:
        return None

    # Step 5: Pick card of chosen rarity (lowest-level-first catch-up)
    rarity_cards = cards_by_rarity[chosen_rarity]
    card_weights = [1.0 / (card.level + 1) for card in rarity_cards]

    chosen_card = _weighted_choice(rarity_cards, card_weights, rng)
    if chosen_card is None:
        return None

    return hero_id, chosen_card.card_id


# ---------------------------------------------------------------------------
# Shared card selection (unchanged)
# ---------------------------------------------------------------------------

def select_shared_card(
    game_state: HeroCardGameState,
    rng: Optional[Random] = None,
) -> Optional[Any]:
    """Select a shared card (Gold/Blue) using lowest-level-first.

    Returns the Card object or None.
    """
    if not game_state.shared_cards:
        return None

    # Sort by level ascending
    sorted_cards = sorted(game_state.shared_cards, key=lambda c: c.level)
    weights = [1.0 / (c.level + 1) for c in sorted_cards]
    total = sum(weights)

    if rng and total > 0:
        roll = rng.random() * total
        cumulative = 0.0
        for card, w in zip(sorted_cards, weights):
            cumulative += w
            if roll <= cumulative:
                return card
        return sorted_cards[-1]
    else:
        return sorted_cards[0]


# ---------------------------------------------------------------------------
# Duplicate computation (unchanged)
# ---------------------------------------------------------------------------

def compute_hero_duplicates(
    card_level: int,
    rng: Optional[Random] = None,
) -> int:
    """Compute duplicates received for a hero card pull.

    Simple model: 1-3 dupes, slightly more at lower levels.
    """
    base = max(1, 4 - card_level // 10)
    if rng:
        return max(1, rng.randint(1, base))
    return max(1, (1 + base) // 2)


# ---------------------------------------------------------------------------
# Joker drop check (unchanged)
# ---------------------------------------------------------------------------

def check_joker_drop(
    config: HeroCardConfig,
    rng: Optional[Random] = None,
) -> bool:
    """Check if a hero joker drops in a regular pack pull."""
    rate = config.joker_drop_rate_in_regular_packs
    if rng:
        return rng.random() < rate
    return rate > 0.5
