| # | guard | slot | skill wired in the BUILT arz | Class | special anim | rig declares | CAN FIRE? |
|---|---|---|---|---|---|---|---|
| 1 | Ravok the Lawless ~ Machae Reaver | skillName4 + specialAttack2 | `minotaur_onslaught.dbr` | Skill_WeaponPool_ChargedLinear | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 2 | Ravok the Lawless ~ Machae Reaver | skillName5 + specialAttack3 | `gigantes_groundbreaker.dbr` | Skill_AttackWave | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 3 | Sethuun ~ Machae Soul-Warden | skillName4 + specialAttack2 | `empusa_spirit_lifedrainnova.dbr` | Skill_AttackProjectileAreaEffect | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 4 | Sethuun ~ Machae Soul-Warden | skillName5 + specialAttack3 | `hero_slowspiritbolt_ring.dbr` | Skill_AttackProjectileRing | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 5 | Bhikru the Bilespitter ~ Machae Venomancer | skillName4 + specialAttack2 | `svc_machaeguard_vomitbile.dbr` | Skill_AttackProjectileBurst | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 6 | Bhikru the Bilespitter ~ Machae Venomancer | skillName5 + specialAttack3 | `svc_machaeguard_venombolt.dbr` | Skill_AttackProjectile | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 7 | Nakoth ~ Machae Plague-Ward | skillName4 + specialAttack2 | `empusa_venom_venomcloud.dbr` | Skill_AttackProjectileAreaEffect | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 8 | Nakoth ~ Machae Plague-Ward | skillName5 + specialAttack3 | `hero_poisonwave.dbr` | Skill_AttackWave | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 9 | Kharzun the Ember ~ Machae Pyre-Ward | skillName4 + specialAttack2 | `empusa_pyro_pillarofflame.dbr` | Skill_AttackProjectileAreaEffect | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 10 | Kharzun the Ember ~ Machae Pyre-Ward | skillName5 + specialAttack3 | `svc_machaeguard_flamewave.dbr` | Skill_AttackWave | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 11 | Voreth ~ Machae Cinder-Reaver | skillName4 + specialAttack2 | `svc_machaeguard_embercharge.dbr` | Skill_AttackWeaponCharge | (none) | heavyshot, slam, strike, thunderclap | **YES** |
| 12 | Voreth ~ Machae Cinder-Reaver | skillName5 + specialAttack3 | `hero_bouncingfire_ring.dbr` | Skill_AttackProjectileRing | (none) | heavyshot, slam, strike, thunderclap | **YES** |

| slot-1 special (all six inherited it dead) | wired to | anim | CAN FIRE? |
|---|---|---|---|
| Ravok the Lawless | `svc_machaeguard_shieldcharge.dbr` (skillName3 `svc_machaeguard_shieldcharge.dbr`) | (none) | **YES** |
| Sethuun | `svc_machaeguard_shieldcharge.dbr` (skillName3 `svc_machaeguard_shieldcharge.dbr`) | (none) | **YES** |
| Bhikru the Bilespitter | `svc_machaeguard_shieldcharge.dbr` (skillName3 `svc_machaeguard_shieldcharge.dbr`) | (none) | **YES** |
| Nakoth | `svc_machaeguard_shieldcharge.dbr` (skillName3 `svc_machaeguard_shieldcharge.dbr`) | (none) | **YES** |
| Kharzun the Ember | `svc_machaeguard_shieldcharge.dbr` (skillName3 `svc_machaeguard_shieldcharge.dbr`) | (none) | **YES** |
| Voreth | `svc_machaeguard_shieldcharge.dbr` (skillName3 `svc_machaeguard_shieldcharge.dbr`) | (none) | **YES** |

=== the 5 blank-anim clones + their SHIPPED donors (shared-record law) ===
  donor hero_vomitbile.dbr                   anim='Belch'         |  clone svc_machaeguard_vomitbile.dbr      anim=''        Class match=True  donor kept 4 non-guard carrier slot(s)
  donor empusavenomancer_venombolt.dbr       anim='Belch'         |  clone svc_machaeguard_venombolt.dbr      anim=''        Class match=True  donor kept 39 non-guard carrier slot(s)
  donor hero_flamewave.dbr                   anim='ShadowScythe'  |  clone svc_machaeguard_flamewave.dbr      anim=''        Class match=True  donor kept 4 non-guard carrier slot(s)
  donor gigantes_shieldcharge.dbr            anim='Charge'        |  clone svc_machaeguard_embercharge.dbr    anim=''        Class match=True  donor kept 6 non-guard carrier slot(s)
  donor shieldcharge.dbr                     anim='ShieldCharge'  |  clone svc_machaeguard_shieldcharge.dbr   anim=''        Class match=True  donor kept 74 non-guard carrier slot(s)
