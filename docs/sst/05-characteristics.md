# Characteristics

Characteristics are filters used by `ChangeTargetAction` to select agents. They can be combined with `And`/`Or`/`Not` logical operators.

## Characteristic Types

### Spatial

| CharacteristicType | Parameters | Description |
|-------------------|-----------|-------------|
| `Position` | `position: Vec2f`, `comp: ComparisonOperator`, `distance: float` | Agent is within distance of position |
| `PositionPolygon` | `polygon: vector<Vec2f>`, `comp: IsIsNot` | Agent is/isn't inside polygon |
| `DistanceToPlayer` | `comp: ComparisonOperator`, `distance: float` | Distance to player meets comparison |
| `DistanceToTarget` | `comp: ComparisonOperator`, `distance: float` | Distance to current target meets comparison |
| `DistanceToModelId` | `comp: ComparisonOperator`, `modelId: uint16_t`, `distance: float` | Distance to agent with model ID meets comparison |
| `AngleToPlayerForward` | `angle: float`, `comp: ComparisonOperator` | Angle to player's forward direction |
| `AngleToCameraForward` | `angle: float`, `comp: ComparisonOperator` | Angle to camera's forward direction |

### Identity

| CharacteristicType | Parameters | Description |
|-------------------|-----------|-------------|
| `Class` | `primary: Class`, `secondary: Class`, `comp: IsIsNot` | Agent's primary/secondary class |
| `Name` | `name: string`, `comp: IsIsNot` | Agent's decoded name |
| `Model` | `modelId: uint16_t`, `comp: IsIsNot` | Agent's model ID |
| `Allegiance` | `agentType: AgentType`, `comp: IsIsNot` | Agent's allegiance (Self/PartyMember/Friendly/Hostile) |
| `IsStoredTarget` | `comp: IsIsNot`, `idRestriction: IdRestriction`, `idRestriction: int` | Agent is/isn't a stored target |

### State

| CharacteristicType | Parameters | Description |
|-------------------|-----------|-------------|
| `HP` | `hp: float`, `comp: ComparisonOperator` | Agent's HP percentage |
| `HPRegen` | `hpRegen: int`, `comp: ComparisonOperator` | Agent's HP regeneration |
| `Speed` | `speed: float`, `comp: ComparisonOperator` | Agent's movement speed |
| `WeaponType` | `weapon: WeaponType`, `comp: IsIsNot` | Agent's equipped weapon type |
| `Status` | `status: Status`, `comp: IsIsNot`, `skillType: SkillType` | Agent's status effect |
| `Skill` | `skill: SkillID`, `comp: IsIsNot` | Agent is casting/has skill active |
| `Bond` | `skill: SkillID`, `comp: IsIsNot` | Agent has bond/communing skill |

### Logical

| CharacteristicType | Parameters | Description |
|-------------------|-----------|-------------|
| `Not` | `characteristic: CharacteristicPtr` | Negate a characteristic |
| `And` | `characteristics: vector<CharacteristicPtr>` | All must match |
| `Or` | `characteristics: vector<CharacteristicPtr>` | Any must match |

## Class Enum

`Any` | `Warrior` | `Ranger` | `Monk` | `Necro` | `Mesmer` | `Elementalist` | `Assassin` | `Ritualist` | `Paragon` | `Dervish`

## AgentType Enum

`Any` | `Self` | `PartyMember` | `Friendly` | `Hostile`

## Status Enum

`Enchanted` | `WeaponSpelled` | `Alive` | `Bleeding` | `Crippled` | `DeepWounded` | `Poisoned` | `Hexed` | `Idle` | `KnockedDown` | `Moving` | `Attacking` | `Casting`

## WeaponType Enum

`Any` | `None` | `Bow` | `Axe` | `Hammer` | `Daggers` | `Scythe` | `Spear` | `Sword` | `Wand` | `Staff`
