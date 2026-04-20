"""Config loader for Variant B — Hero Card System.

Provides default configuration with sample heroes, card pools, skill trees,
premium packs, and upgrade tables. All values are editable from the frontend.
Supports saving/loading persisted configs to data/defaults/variant_b_config.json.
"""

from __future__ import annotations

import logging
from pathlib import Path

from simulation.models import UserProfile

from simulation.variants.variant_b.models import (
    HeroCardConfig,
    HeroCardDef,
    HeroCardRarity,
    HeroDef,
    HeroDuplicateRange,
    HeroDropConfig,
    HeroUpgradeCostTable,
    HeroCardTypesRange,
    HeroPackType,
    PremiumPackAdditionalReward,
    PremiumPackCardRate,
    PremiumPackDef,
    PremiumPackPullRarity,
    PremiumPackSchedule,
    SharedDuplicateRange,
    SharedUpgradeCostTable,
    SkillTreeNode,
)


def load_defaults() -> HeroCardConfig:
    """Load Variant B config — from saved file if available, else built-in defaults."""
    saved = load_saved_config()
    if saved is not None:
        return saved
    return _builtin_defaults()


def _builtin_defaults() -> HeroCardConfig:
    """Built-in default Variant B configuration with all 17 heroes (24 cards each, 408 total)."""
    heroes = [
        _create_sample_hero("woody", "Woody", num_cards=24),
        _create_sample_hero("cowboy", "Cowboy", num_cards=24),
        _create_sample_hero("barbarian", "Barbarian", num_cards=24),
        _create_sample_hero("rexx", "Rexx", num_cards=24),
        _create_sample_hero("sunna", "Sunna", num_cards=24),
        _create_sample_hero("mammon", "Mammon", num_cards=24),
        _create_sample_hero("rogue", "Rogue", num_cards=24),
        _create_sample_hero("felorc", "Felorc", num_cards=24),
        _create_sample_hero("eiva", "Eiva", num_cards=24),
        _create_sample_hero("gudan", "Gudan", num_cards=24),
        _create_sample_hero("druid", "Druid", num_cards=24),
        _create_sample_hero("yasuhiro", "Yasuhiro", num_cards=24),
        _create_sample_hero("nova", "Nova", num_cards=24),
        _create_sample_hero("rickie", "Rickie", num_cards=24),
        _create_sample_hero("raven", "Raven", num_cards=24),
        _create_sample_hero("jester", "Jester", num_cards=24),
        _create_sample_hero("munara", "Munara", num_cards=24),
    ]

    # One premium pack per hero (card pool auto-derived from hero's cards)
    premium_packs = [
        _create_hero_pack(hero) for hero in heroes
    ]

    return HeroCardConfig(
        num_days=730,
        initial_coins=0,
        initial_bluestars=0,
        heroes=heroes,
        hero_unlock_schedule={
            # Year 1
            0: ["woody", "cowboy"],
            14: ["barbarian"],
            30: ["rexx"],
            50: ["sunna"],
            75: ["mammon"],
            100: ["rogue"],
            130: ["felorc"],
            170: ["eiva"],
            220: ["gudan"],
            280: ["druid"],
            340: ["yasuhiro"],
            # Year 2
            400: ["nova"],
            460: ["rickie"],
            530: ["raven"],
            600: ["jester"],
            680: ["munara"],
        },
        num_gold_cards=9,
        num_blue_cards=14,
        num_gray_cards=20,
        hero_upgrade_tables=_default_upgrade_tables(),
        hero_duplicate_ranges=_default_duplicate_ranges(),
        shared_upgrade_tables=_default_shared_upgrade_tables(),
        shared_duplicate_ranges=_default_shared_duplicate_ranges(),
        shared_xp_per_level=[50 + i * 25 for i in range(30)],
        shared_max_hero_level=30,
        joker_drop_rate_in_regular_packs=0.01,
        drop_config=HeroDropConfig(
            hero_vs_shared_base_rate=0.50,
            pity_counter_threshold=10,
        ),
        pack_types=[
            HeroPackType(name="StandardPackT1", card_types_table={
                0: HeroCardTypesRange(min=1, max=2),
                100: HeroCardTypesRange(min=1, max=2),
                200: HeroCardTypesRange(min=1, max=2),
                350: HeroCardTypesRange(min=1, max=2),
                500: HeroCardTypesRange(min=1, max=2),
            }),
            HeroPackType(name="StandardPackT2", card_types_table={
                0: HeroCardTypesRange(min=1, max=2),
                100: HeroCardTypesRange(min=1, max=2),
                200: HeroCardTypesRange(min=1, max=3),
                350: HeroCardTypesRange(min=1, max=3),
                500: HeroCardTypesRange(min=1, max=3),
            }),
            HeroPackType(name="StandardPackT3", card_types_table={
                0: HeroCardTypesRange(min=1, max=3),
                100: HeroCardTypesRange(min=1, max=3),
                200: HeroCardTypesRange(min=2, max=3),
                350: HeroCardTypesRange(min=2, max=3),
                500: HeroCardTypesRange(min=2, max=3),
            }),
            HeroPackType(name="StandardPackT4", card_types_table={
                0: HeroCardTypesRange(min=1, max=3),
                100: HeroCardTypesRange(min=1, max=3),
                200: HeroCardTypesRange(min=2, max=4),
                350: HeroCardTypesRange(min=2, max=4),
                500: HeroCardTypesRange(min=2, max=4),
            }),
            HeroPackType(name="StandardPackT5", card_types_table={
                0: HeroCardTypesRange(min=3, max=5),
                100: HeroCardTypesRange(min=3, max=5),
                200: HeroCardTypesRange(min=4, max=5),
                350: HeroCardTypesRange(min=4, max=5),
                500: HeroCardTypesRange(min=4, max=5),
            }),
            HeroPackType(name="EndOfChapterPack", card_types_table={
                0: HeroCardTypesRange(min=1, max=2),
                100: HeroCardTypesRange(min=1, max=2),
                200: HeroCardTypesRange(min=1, max=2),
                350: HeroCardTypesRange(min=1, max=2),
                500: HeroCardTypesRange(min=1, max=2),
            }),
            HeroPackType(name="PetPack", card_types_table={
                0: HeroCardTypesRange(min=1, max=2),
                100: HeroCardTypesRange(min=1, max=2),
                200: HeroCardTypesRange(min=2, max=3),
                350: HeroCardTypesRange(min=2, max=3),
                500: HeroCardTypesRange(min=2, max=4),
            }),
            HeroPackType(name="HeroPack", card_types_table={
                0: HeroCardTypesRange(min=1, max=2),
                100: HeroCardTypesRange(min=1, max=2),
                200: HeroCardTypesRange(min=2, max=3),
                350: HeroCardTypesRange(min=2, max=3),
                500: HeroCardTypesRange(min=2, max=4),
            }),
            HeroPackType(name="GearPack", card_types_table={
                0: HeroCardTypesRange(min=1, max=2),
                100: HeroCardTypesRange(min=1, max=2),
                200: HeroCardTypesRange(min=2, max=3),
                350: HeroCardTypesRange(min=2, max=3),
                500: HeroCardTypesRange(min=2, max=4),
            }),
        ],
        daily_pack_schedule=[
            {
                "StandardPackT1": 1.0, "StandardPackT2": 1.0, "StandardPackT3": 1.0,
                "StandardPackT4": 1.0, "StandardPackT5": 1.0,
                "PetPack": 1.0, "GearPack": 1.0, "HeroPack": 1.0,
                "EndOfChapterPack": 1.0,
            },
        ],
        premium_packs=premium_packs,
        premium_pack_schedule=[
            PremiumPackSchedule(pack_id=hero.hero_id, available_from_day=0, available_until_day=100)
            for hero in heroes
        ],
    )


def _create_sample_hero(hero_id: str, name: str, num_cards: int = 24) -> HeroDef:
    """Create a hero with a balanced card pool and real skill tree pattern.

    Default: 24 cards per hero (17 heroes x 24 = 408 total).
    12 starter cards (all GRAY), 12 unlocked via skill tree.
    Rarity distribution and skill tree are fully editable in the UI.
    """
    # Distribute cards across rarities: ~50% gray, 30% blue, 20% gold
    num_gray = max(1, round(num_cards * 0.50))   # 12
    num_blue = max(1, round(num_cards * 0.30))    # 7
    num_gold = max(1, num_cards - num_gray - num_blue)  # 5
    rarity_dist = [
        (HeroCardRarity.GRAY, num_gray),
        (HeroCardRarity.BLUE, num_blue),
        (HeroCardRarity.GOLD, num_gold),
    ]

    cards = []
    xp_values = {
        HeroCardRarity.GRAY: 5,
        HeroCardRarity.BLUE: 15,
        HeroCardRarity.GOLD: 40,
    }
    card_idx = 1
    for rarity, count in rarity_dist:
        for j in range(count):
            cards.append(HeroCardDef(
                card_id=f"{hero_id}_card_{card_idx}",
                hero_id=hero_id,
                rarity=rarity,
                name=f"{name} {rarity.value.title()} {j+1}",
                base_xp_on_upgrade=xp_values[rarity],
            ))
            card_idx += 1

    # Starter cards: all GRAY cards (12 starters)
    starter_ids = [c.card_id for c in cards if c.rarity == HeroCardRarity.GRAY]

    # Remaining 12 cards (BLUE + GOLD) unlock via skill tree
    remaining_cards = [c.card_id for c in cards if c.card_id not in starter_ids]

    # Skill tree pattern (matches real game design):
    # Levels where a card unlocks: 4, 6, 8, 10, 11, 13, 15, 17, 19, 21, 22, 24
    # Other levels have stat boosts, hero passives, deck size, etc.
    _TREE_TEMPLATE = [
        # (level, reward_type)  — "card" means pop a card from remaining
        (2, "Stat Boosts"),
        (3, "Stat Boosts"),
        (4, "card"),
        (5, "Hero Passive"),
        (6, "card"),
        (7, "+1 Battle Deck Size"),
        (8, "card"),
        (9, "Hero Passive"),
        (10, "card"),
        (11, "card"),
        (12, "+1 Battle Deck Size"),
        (13, "card"),
        (14, "Hero Passive"),
        (15, "card"),
        (16, "Perma Slot Upgrade"),
        (17, "card"),
        (18, "Hero Passive"),
        (19, "card"),
        (20, "+1 Battle Deck Size"),
        (21, "card"),
        (22, "card"),
        (23, "Hero Passive"),
        (24, "card"),
        (25, "All Heroes Stat Boost"),
        (26, "Ascension Shards"),
        (27, "All Heroes Stat Boost"),
        (28, "Ascension Shards"),
        (29, "All Heroes Stat Boost"),
        (30, "Ascension Shards"),
    ]

    skill_tree = []
    card_queue = list(remaining_cards)
    for node_idx, (level_req, reward) in enumerate(_TREE_TEMPLATE):
        if reward == "card" and card_queue:
            unlocked = [card_queue.pop(0)]
            perk = f"Unlockable Card"
        else:
            unlocked = []
            perk = reward
        skill_tree.append(SkillTreeNode(
            node_index=node_idx,
            hero_level_required=level_req,
            cards_unlocked=unlocked,
            perk_label=perk,
        ))

    # XP per level: escalating thresholds (30 levels)
    xp_per_level = [50 + i * 25 for i in range(30)]

    return HeroDef(
        hero_id=hero_id,
        name=name,
        card_pool=cards,
        skill_tree=skill_tree,
        xp_per_level=xp_per_level,
        max_level=30,
        starter_card_ids=starter_ids,
    )


def _create_hero_pack(hero: HeroDef) -> PremiumPackDef:
    """Create one premium pack for a hero using per-pull rarity weights."""
    return PremiumPackDef(
        pack_id=hero.hero_id,
        name=f"{hero.name} Card Pack",
        featured_hero_ids=[hero.hero_id],
        min_cards_per_pack=4,
        max_cards_per_pack=4,
        diamond_cost=500,
        joker_rate=0.02,
        gold_guarantee=True,
        hero_tokens_per_pack=5,
        additional_rewards=[
            PremiumPackAdditionalReward(reward_type="coins", amount=500, probability=0.20),
            PremiumPackAdditionalReward(reward_type="bluestars", amount=50, probability=0.10),
        ],
        pull_rarity_schedule=[
            PremiumPackPullRarity(gray_weight=0.60, blue_weight=0.30, gold_weight=0.10),
            PremiumPackPullRarity(gray_weight=0.15, blue_weight=0.75, gold_weight=0.10),
            PremiumPackPullRarity(gray_weight=0.15, blue_weight=0.75, gold_weight=0.10),
            PremiumPackPullRarity(gray_weight=0.00, blue_weight=0.00, gold_weight=1.00),
        ],
        default_rarity_weights=PremiumPackPullRarity(gray_weight=0.60, blue_weight=0.30, gold_weight=0.10),
    )


_log = logging.getLogger(__name__)


def _get_saved_config_path() -> Path:
    """Path to the persisted Variant B config file."""
    return Path(__file__).resolve().parent.parent.parent.parent / "data" / "defaults" / "variant_b_config.json"


def load_saved_config() -> HeroCardConfig | None:
    """Load persisted Variant B config from disk, or None if not found."""
    path = _get_saved_config_path()
    if not path.exists():
        return None
    try:
        return HeroCardConfig.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _log.warning("Failed to load saved Variant B config: %s", exc)
        return None


def save_config(config: HeroCardConfig) -> None:
    """Persist the current Variant B config to disk."""
    path = _get_saved_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config.model_dump_json(indent=2), encoding="utf-8")


def _default_upgrade_tables() -> list[HeroUpgradeCostTable]:
    """Create default upgrade cost tables for each rarity (9 card levels)."""
    return [
        HeroUpgradeCostTable(
            rarity=HeroCardRarity.GRAY,
            duplicate_costs=[10, 12, 13, 28, 32, 40, 48, 78, 150],
            coin_costs=[250, 375, 500, 625, 750, 875, 1000, 1125, 1250],
            bluestar_rewards=[50, 65, 80, 95, 110, 125, 150, 200, 250],
            xp_rewards=[10, 10, 10, 20, 20, 20, 20, 30, 30],
        ),
        HeroUpgradeCostTable(
            rarity=HeroCardRarity.BLUE,
            duplicate_costs=[20, 24, 26, 55, 64, 80, 90, 160, 300],
            coin_costs=[250, 375, 500, 625, 750, 875, 1000, 1125, 1250],
            bluestar_rewards=[100, 130, 160, 190, 220, 250, 300, 400, 500],
            xp_rewards=[20, 20, 20, 40, 40, 40, 40, 60, 60],
        ),
        HeroUpgradeCostTable(
            rarity=HeroCardRarity.GOLD,
            duplicate_costs=[20, 30, 36, 80, 90, 100, 120, 220, 240],
            coin_costs=[250, 375, 500, 625, 750, 875, 1000, 1125, 1250],
            bluestar_rewards=[150, 195, 240, 285, 330, 375, 450, 600, 750],
            xp_rewards=[30, 30, 30, 60, 60, 60, 60, 90, 90],
        ),
    ]


def _default_duplicate_ranges() -> list[HeroDuplicateRange]:
    """Default duplicate % ranges for hero card pulls, per rarity.

    When a hero card is pulled, dupes received = round(dupe_cost_for_next_level * pct),
    where pct is drawn uniformly from [min_pct, max_pct] for that card's current level.

    Percentages decrease as card level increases — early levels are easier to upgrade.
    9 entries (one per card level, index 0 = level 1).
    """
    return [
        HeroDuplicateRange(
            rarity=HeroCardRarity.GRAY,
            min_pct=[0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40],
            max_pct=[0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50],
            coins_per_dupe=[25, 29, 35, 21, 22, 20, 19, 13, 8],
        ),
        HeroDuplicateRange(
            rarity=HeroCardRarity.BLUE,
            min_pct=[0.65, 0.60, 0.55, 0.50, 0.40, 0.35, 0.30, 0.20, 0.10],
            max_pct=[0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.30, 0.20],
            coins_per_dupe=[13, 15, 18, 11, 11, 10, 10, 7, 4],
        ),
        HeroDuplicateRange(
            rarity=HeroCardRarity.GOLD,
            min_pct=[0.25, 0.25, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05, 0.05],
            max_pct=[0.40, 0.40, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15],
            coins_per_dupe=[13, 12, 13, 8, 8, 8, 8, 5, 5],
        ),
    ]


def _default_shared_upgrade_tables() -> list[SharedUpgradeCostTable]:
    """Default upgrade cost tables for shared cards (99 levels per category).

    Shared card upgrades grant bluestars but NO hero XP.
    """
    num_levels = 99

    def _make_dupe_costs(base: int, increment: int) -> list[int]:
        return [base + i * increment for i in range(num_levels)]

    def _make_coin_costs(base: int, increment: int) -> list[int]:
        return [base + i * increment for i in range(num_levels)]

    def _make_bluestar_rewards(base: int, step_every: int, step_amount: int) -> list[int]:
        return [base + (i // step_every) * step_amount for i in range(num_levels)]

    blue_gray_dupes = [15 + i * 3 for i in range(num_levels)]
    blue_gray_bluestars = [
        10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 20, 25, 25, 25,
        25, 25, 25, 30, 30, 30, 30, 30, 30, 35, 35, 35, 35, 35, 35, 40, 40, 40, 40, 40,
        40, 45, 45, 45, 45, 45, 45, 45, 50, 50, 50, 50, 50, 50, 50, 55, 55, 55, 55, 55,
        55, 55, 60, 60, 60, 60, 60, 60, 60, 65, 65, 65, 65, 65, 65, 65, 70, 70, 70, 70,
        70, 70, 70, 75, 75, 75, 75, 75, 75, 75, 75, 80, 80, 80, 80, 80, 80, 80, 80,
    ]

    return [
        SharedUpgradeCostTable(
            category="GRAY_SHARED",
            duplicate_costs=blue_gray_dupes,
            coin_costs=_make_coin_costs(50, 50),
            bluestar_rewards=blue_gray_bluestars,
        ),
        SharedUpgradeCostTable(
            category="BLUE_SHARED",
            duplicate_costs=blue_gray_dupes,
            coin_costs=_make_coin_costs(50, 50),
            bluestar_rewards=blue_gray_bluestars,
        ),
        SharedUpgradeCostTable(
            category="GOLD_SHARED",
            duplicate_costs=[10 + i for i in range(num_levels)],
            coin_costs=_make_coin_costs(50, 50),
            bluestar_rewards=_make_bluestar_rewards(30, 5, 5),
        ),
    ]


def _default_shared_duplicate_ranges() -> list[SharedDuplicateRange]:
    """Default duplicate % ranges for shared card pulls, per category.

    99 entries per category (one per card level). Same values for all shared categories.
    """
    # Stepped taper matching the user-specified breakpoints
    shared_min_pct = (
        [0.80] * 10 + [0.70] * 19 + [0.65] * 11 + [0.60] * 9 +
        [0.55] * 11 + [0.50] * 20 + [0.40] * 19
    )
    shared_max_pct = (
        [0.90] * 10 + [0.80] * 19 + [0.75] * 11 + [0.70] * 9 +
        [0.65] * 11 + [0.60] * 20 + [0.60] * 19
    )
    shared_coins = [
        5, 8, 9, 11, 13, 14, 15, 16, 17, 18,
        18, 19, 20, 20, 20, 21, 21, 22, 22, 22,
        23, 23, 23, 23, 24, 24, 24, 24, 24, 24,
        25, 25, 25, 25, 25, 25, 25, 25, 26, 26,
        26, 26, 26, 26, 26, 26, 26, 26, 26, 27,
        27, 27, 27, 27, 27, 27, 27, 27, 27, 27,
        27, 27, 27, 27, 27, 27, 27, 27, 27, 28,
        28, 28, 28, 28, 28, 28, 28, 28, 28, 28,
        28, 28, 28, 28, 28, 28, 28, 28, 28, 28,
        28, 28, 28, 28, 28, 28, 28, 28, 28,
    ]

    return [
        SharedDuplicateRange(
            category="GRAY_SHARED",
            min_pct=shared_min_pct, max_pct=shared_max_pct,
            coins_per_dupe=shared_coins,
        ),
        SharedDuplicateRange(
            category="BLUE_SHARED",
            min_pct=shared_min_pct, max_pct=shared_max_pct,
            coins_per_dupe=shared_coins,
        ),
        SharedDuplicateRange(
            category="GOLD_SHARED",
            min_pct=shared_min_pct, max_pct=shared_max_pct,
            coins_per_dupe=shared_coins,
        ),
    ]


# ── Variant B profile CRUD ───────────────────────────────────────────────────

def _get_vb_profiles_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "profiles_variant_b"


def list_vb_profiles() -> list[str]:
    d = _get_vb_profiles_dir()
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


def load_vb_profile(name: str) -> UserProfile:
    path = _get_vb_profiles_dir() / f"{name}.json"
    return UserProfile.model_validate_json(path.read_text(encoding="utf-8"))


def save_vb_profile(profile: UserProfile) -> None:
    d = _get_vb_profiles_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{profile.name}.json"
    path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")


def delete_vb_profile(name: str) -> None:
    path = _get_vb_profiles_dir() / f"{name}.json"
    if path.exists():
        path.unlink()
