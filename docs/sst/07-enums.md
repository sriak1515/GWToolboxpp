# Enums Reference

## Trigger
`None` | `InstanceLoad` | `HardModePing` | `Hotkey` | `ChatMessage` | `BeginSkillCast` | `BeginCooldown` | `SkillCastInterrupt` | `DisplayDialog` | `DungeonReward` | `DoaZoneComplete`

## ComparisonOperator
`Equals` | `Less` | `Greater` | `LessOrEqual` | `GreaterOrEqual` | `NotEquals`

## Channel (for SendChat)
`All` | `Guild` | `Team` | `Trade` | `Alliance` | `Whisper` | `Emote` | `Log`

## QuestStatus
`NotStarted` | `Running` | `Completed` | `Failed`

## GoToTargetFinishCondition
`None` | `StoppedMovingNextToTarget` | `DialogOpen`

## HasSkillRequirement
`OnBar` | `OffCooldown` | `ReadyToUse`

## PlayerConnectednessRequirement
`All` | `Individual`

## EquippedItemSlot
`Mainhand` | `Offhand` | `Chest` | `Legs` | `Head` | `Feet` | `Hands`

## Bag
`Backpack` | `BeltPouch` | `Bag1` | `Bag2` | `EquipmentPack`

## IsIsNot
`Is` | `IsNot`

## TrueFalse
`True` | `False`

## MoveToBehaviour
`SendOnce` | `RepeatIfIdle` | `ImmediateFinish`

## ReferenceFrame
`Player` | `Camera`

## AnyNoYes
`Any` | `No` | `Yes`

## Sorting (for ChangeTarget)
`AgentId` | `ClosestToPlayer` | `FurthestFromPlayer` | `ClosestToTarget` | `FurthestFromTarget` | `LowestHp` | `HighestHp` | `ModelID`

## AgentType
`Any` | `Self` | `PartyMember` | `Friendly` | `Hostile`

## DoorStatus
`Open` | `Closed`

## Area
`Urgoz` | `Deep` | `Doa`

## DoaZone
`Foundry` (0x273F) | `Veil` (0x2740) | `Gloom` (0x2741) | `City` (0x2742)

## MovementDirection
`Forwards` | `Left` | `Right` | `Backwards`

## SkillType
`Any` | `Spell` | `Signet` | `Well` | `Skill` | `Ward` | `Glyph` | `Attack` | `Preparation` | `Trap` | `Ritual` | `WeaponSpell` | `Chant` | `Hex` | `Enchantment`

## ObjectiveType
`Quest` | `Mission`

## IdRestriction
`Any` | `SpecificId`

## WeaponType
`Any` | `None` | `Bow` | `Axe` | `Hammer` | `Daggers` | `Scythe` | `Spear` | `Sword` | `Wand` | `Staff`

## Status
`Enchanted` | `WeaponSpelled` | `Alive` | `Bleeding` | `Crippled` | `DeepWounded` | `Poisoned` | `Hexed` | `Idle` | `KnockedDown` | `Moving` | `Attacking` | `Casting`

## Class
`Any` | `Warrior` | `Ranger` | `Monk` | `Necro` | `Mesmer` | `Elementalist` | `Assassin` | `Ritualist` | `Paragon` | `Dervish`

## DoorID

### Urgoz
`Urgoz_zone_2` (45420) | `Urgoz_zone_3` (11692) | `Urgoz_zone_4` (54552) | `Urgoz_zone_5` (1760) | `Urgoz_zone_6` (40330) | `Urgoz_zone_7` (60114) | `Urgoz_zone_8` (37191) | `Urgoz_zone_9` (35500) | `Urgoz_zone_10` (34278) | `Urgoz_zone_11` (15529)

### Deep
`Deep_room_1_first` (12669) | `Deep_room_1_second` (11692) | `Deep_room_2_first` (54552) | `Deep_room_2_second` (1760) | `Deep_room_3_first` (45425) | `Deep_room_3_second` (48290) | `Deep_room_4_first` (40330) | `Deep_room_4_second` (60114) | `Deep_room_5` (29594) | `Deep_room_6` (49742) | `Deep_room_7` (55680) | `Deep_room_9` (99887) | `Deep_room_11` (28961)

### DoA
`DoA_foundry_entrance_r1` (39534) | `DoA_foundry_r1_r2` (6356) | `DoA_foundry_r2_r3` (45276) | `DoA_foundry_r3_r4` (55421) | `DoA_foundry_r4_r5` (49719) | `DoA_foundry_r5_bb` (45667) | `DoA_foundry_behind_bb` (1731) | `DoA_city_entrance` (63939) | `DoA_city_wall` (54727) | `DoA_city_jadoth` (64556) | `DoA_veil_360_left` (13005) | `DoA_veil_360_middle` (11772) | `DoA_veil_360_right` (28851) | `DoA_veil_derv` (56510) | `DoA_veil_ranger` (4753) | `DoA_veil_trench_necro` (46650) | `DoA_veil_trench_mes` (29594) | `DoA_veil_trench_ele` (49742) | `DoA_veil_trench_monk` (55680) | `DoA_veil_trench_gloom` (28961) | `DoA_veil_to_gloom` (3) | `DoA_gloom_to_foundry` (17955) | `DoA_gloom_rift` (47069)
