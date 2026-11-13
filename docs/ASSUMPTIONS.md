# Assumptions register: the casualty generator

Every number the generator uses or must reproduce, one row per parameter in `params.yaml`. A row marked
**Assumed: true** is a modelling choice, not a measured or published value; a notebook that quotes one is
quoting an assumption. Every other row traces to an evidence id in [`EVIDENCE.md`](EVIDENCE.md), and
"provisional" marks a source read only from a search extract (CARRIED). **Used in** lists the notebooks
that draw on the parameter.

This file is generated from the provenance graph by `python -m inference_labs.graph.provenance`. Do not edit
it by hand: change `params.yaml` and regenerate.

| Dataset | Parameter | Value | Unit | Source | Assumed | Used in |
|---|---|---|---|---|---|---|
| generator | `stream_shares`: Share of admissions by stream | disease 0.44, battle 0.3, non_battle 0.27 | share of admissions | E-34, E-35, E-36 | false | — |
| generator | `battle_mechanism`: Mechanism of battle injury | explosion 1164, small_arms 974, other 133 | count (used as a ratio) | E-35 | false | — |
| generator | `non_battle_mechanism`: Mechanism of non-battle injury | other 1949, small_arms 52, explosion 18 | count (used as a ratio) | E-35 | false | — |
| generator | `battle_patient_type`: Patient type among battle casualties | haemorrhage 0.6, chest 0.2, head 0.2 | share of battle casualties | assumption | true | — |
| generator | `significant_bleeding_given_haemorrhage`: Share of haemorrhage-type casualties who are bleeding significantly | 0.6 | probability | assumption | true | — |
| generator | `site_given_mechanism`: Site of the wound in haemorrhage-type casualties, by mechanism | explosion (truncal 0.25, junctional 0.15, extremity 0.6); small_arms (truncal 0.47, junctional 0.15, extremity 0.38); other (truncal 0.35, junctional 0.15, extremity 0.5) | share of haemorrhage-type casualties | assumption | true | — |
| generator | `pneumothorax_given_chest`: Share of chest-injury casualties with a pneumothorax | 0.6 | probability | assumption | true | — |
| generator | `tension_given_pneumothorax`: Share of pneumothoraces under tension, needing a life-saving intervention | 0.5 | probability | assumption | true | — |
| generator | `severe_given_head`: Share of head-injury casualties with a severe injury needing a life-saving intervention | 0.4 | probability | assumption | true | — |
| generator | `sepsis_given_disease`: Share of disease admissions with sepsis | 0.1 | probability | assumption | true | — |
| generator | `septic_shock_given_sepsis`: Share of sepsis cases in septic shock, needing a life-saving intervention | 0.4 | probability | assumption | true | — |
| generator | `triage_accuracy_military`: MPTT-24 Priority One against need for a life-saving intervention, military registry | sensitivity 0.667, specificity 0.699 | proportion | E-09 | false | — |
| generator | `triage_accuracy_civilian`: MPTT-24 Priority One against need for a life-saving intervention, civilian registry | sensitivity 0.535, specificity 0.748 | proportion | E-09 | false | — |
| generator | `heart_rate`: Heart rate, normal around a resting mean, raised by injury and by each condition present | resting 80; injury 12; effect (bleeding 3, bleeding_by_severity_centile 15, tension_pneumothorax 11, sepsis 7, septic_shock 7); residual_sd 20 | beats per minute (normal; rounded to whole beats) | assumption | true | — |
| generator | `respiratory_rate`: Respiratory rate, normal around a resting mean, raised by injury and by each condition present | resting 16; injury 5; effect (bleeding 1, bleeding_by_severity_centile 4, tension_pneumothorax 4, sepsis 2, septic_shock 2); residual_sd 4 | breaths per minute (normal; rounded to whole breaths) | assumption | true | — |
| generator | `respiratory_rate_severe_head_injury`: Share of severe head injuries in which breathing is slowed, and the factor applied to the rate | share_slowed 0.4, factor 0.5 | probability; multiplier | assumption | true | — |
| generator | `avpu_severe_head_injury`: Conscious level on the AVPU scale in a severe head injury | A 0.3, V 0.3, P 0.25, U 0.15 | share of severe head injuries | assumption | true | — |
| generator | `avpu_not_alert_base`: Chance that a casualty without a severe head injury is not alert, whatever else is wrong | 0.06 | probability | assumption | true | — |
| generator | `avpu_bleeding`: In significant bleeding, a further chance of not being alert that rises as systolic pressure falls | even_odds_at_sbp 70, log_odds_per_10_mmhg -1.2 | mm Hg; log odds per 10 mm Hg | assumption | true | — |
| generator | `avpu_levels_not_alert`: Level of response in a casualty without a severe head injury who is not alert | V 0.5, P 0.3, U 0.2 | share of casualties not alert | assumption | true | — |
| generator | `walking`: Share walking, by need for a life-saving intervention, among casualties who respond to voice or better | no_intervention 0.55, needs_intervention 0.3 | probability | assumption | true | — |
| generator | `catastrophic_haemorrhage_share`: Share of casualties bleeding significantly from an extremity or junction who have catastrophic external haemorrhage | 0.15 | probability | assumption | true | — |
| generator | `cohort_mix_civilian`: Civilian cohort's default share by stream | disease 0, battle 0, non_battle 1 | share of the cohort | assumption | true | — |
| generator | `cohort_mechanism_civilian`: Mechanism of injury in the civilian cohort | other 0.94, small_arms 0.03, explosion 0.03 | share of the civilian cohort | assumption | true | — |
| generator | `cohort_patient_type_civilian`: Patient type in the civilian cohort | haemorrhage 0.15, chest 0.15, head 0.2, dnbi 0.5 | share of the civilian cohort | assumption | true | — |
| generator | `cohort_physiology_civilian`: Civilian cohort against the military reference, the shift in heart rate and the scale on the effects of bleeding, tension pneumothorax, sepsis and septic shock on heart and respiratory rate | heart_rate_shift -6, response_scale 0.35 | beats per minute; multiplier | assumption | true | — |
| generator | `sbp_not_bleeding`: Systolic pressure in casualties not bleeding significantly | mean 125, sd 12 | mm Hg | assumption | true | — |
| generator | `sbp_bleeding`: Systolic pressure in bleeding casualties, falling with severity | mean 105, severity_slope -12, residual_sd 12 | mm Hg | assumption | true | — |
| generator | `scan_accuracy_in_hospital`: eFAST accuracy in hospital | free_fluid (sensitivity 0.74, specificity 0.98); pneumothorax (sensitivity 0.69, specificity 0.99) | proportion | E-14 | false | — |
| generator | `scan_accuracy_pre_hospital`: eFAST accuracy before hospital | free_fluid (sensitivity 0.25, specificity 0.96); pneumothorax (sensitivity 0.38, specificity 0.96) | proportion | E-16 | false | — |
| generator | `time_to_phec_min`: Time from injury to pre-hospital emergency care, when tranexamic acid is given | median 56, log_sd 0.5 | minutes (lognormal) | assumption | true | — |
| generator | `phec_to_role2_min`: Time from pre-hospital emergency care to arrival at Role 2 | median 50, log_sd 0.4 | minutes (lognormal) | assumption | true | — |
| generator | `lethal_haemorrhage_site`: Site of bleeding among deaths from bleeding | truncal 0.673, junctional 0.192, extremity 0.135 | share of bleeding deaths | E-41 | false | — |
| generator | `bleeding_death_hazard`: Hourly death rate from bleeding, at 1, 6 and 9 hours | h_1h 0.046, h_6h 0.01, h_9h 0.001 | deaths per casualty-hour at risk | E-85 | false | — |
| generator | `bleeding_death_severity_log_odds`: Change in the log odds of bleeding death per standard deviation of severity | 0.75 | log odds per standard deviation | assumption | true | — |
| generator | `txa_allocation`: Share of battle casualties allocated tranexamic acid, at random | 0.5 | probability | assumption | true | — |
| generator | `txa_benefit_at_zero_delay`: Relative reduction in bleeding death from tranexamic acid given at the moment of injury | 0.41 | relative reduction | assumption | true | — |
| generator | `txa_rr_by_delay`: Relative risk of bleeding death with tranexamic acid, by time from injury to treatment | up_to_1h 0.68, from_1h_to_3h 0.79, over_3h 1.44 | relative risk | E-22 | false | — |
| generator | `txa_benefit_decay`: Decline of the benefit of tranexamic acid with delay | decline_per_15min 0.1, none_after_h 3 | share of the benefit at zero delay; hours | E-24 | false | — |
