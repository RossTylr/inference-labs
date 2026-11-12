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
| generator | `mptt24_thresholds`: MPTT-24 physiological thresholds the generated physiology must not straddle | respiratory_rate_below 12, respiratory_rate_at_or_above 24, heart_rate_at_or_above 100 | breaths or beats per minute | E-04, E-08 | false | — |
| generator | `walking_given_not_priority_one`: Share of casualties not in Priority One who are walking | 0.6 | probability | assumption | true | — |
| generator | `catastrophic_haemorrhage_share`: Share of Priority One casualties bleeding from an extremity or junction who have catastrophic external haemorrhage | 0.5 | probability | assumption | true | — |
| generator | `abnormal_sign_weights`: Which vital sign is abnormal in a Priority One casualty | heart_rate 0.5, respiratory_rate 0.3, avpu 0.2 | share of Priority One casualties | assumption | true | — |
| generator | `heart_rate_ranges`: Range of heart rate, normal and abnormal, drawn uniformly in whole beats | normal 60 to 99, abnormal 101 to 150 | beats per minute | assumption | true | — |
| generator | `respiratory_rate_ranges`: Range of respiratory rate, normal, abnormally low and abnormally high, drawn uniformly in whole breaths | normal 12 to 21, low 6 to 10, high 25 to 40 | breaths per minute | assumption | true | — |
| generator | `respiratory_rate_low_share`: Share of abnormal respiratory rates that are low | 0.2 | probability | assumption | true | — |
| generator | `avpu_abnormal_shares`: Level of response when it is abnormal | V 0.5, P 0.3, U 0.2 | share of casualties not alert | assumption | true | — |
| generator | `sbp_not_bleeding`: Systolic pressure in casualties not bleeding significantly | mean 125, sd 12 | mm Hg | assumption | true | — |
| generator | `sbp_bleeding`: Systolic pressure in bleeding casualties, falling with severity | mean 105, severity_slope -12, residual_sd 12 | mm Hg | assumption | true | — |
| generator | `scan_accuracy_in_hospital`: eFAST accuracy in hospital | free_fluid (sensitivity 0.74, specificity 0.98); pneumothorax (sensitivity 0.69, specificity 0.99) | proportion | E-14 (provisional) | false | — |
| generator | `scan_accuracy_pre_hospital`: eFAST accuracy before hospital | free_fluid (sensitivity 0.25, specificity 0.96); pneumothorax (sensitivity 0.38, specificity 0.96) | proportion | E-16 (provisional) | false | — |
| generator | `time_to_phec_min`: Time from injury to pre-hospital emergency care, when tranexamic acid is given | median 56, log_sd 0.5 | minutes (lognormal) | assumption | true | — |
| generator | `phec_to_role2_min`: Time from pre-hospital emergency care to arrival at Role 2 | median 50, log_sd 0.4 | minutes (lognormal) | assumption | true | — |
| generator | `lethal_haemorrhage_site`: Site of bleeding among deaths from bleeding | truncal 0.673, junctional 0.192, extremity 0.135 | share of bleeding deaths | E-41 | false | — |
| generator | `bleeding_death_hazard`: Hourly death rate from bleeding, at 1, 6 and 9 hours | h_1h 0.046, h_6h 0.01, h_9h 0.001 | deaths per casualty-hour at risk | E-85 | false | — |
| generator | `bleeding_death_severity_log_odds`: Change in the log odds of bleeding death per standard deviation of severity | 0.75 | log odds per standard deviation | assumption | true | — |
| generator | `txa_allocation`: Share of battle casualties allocated tranexamic acid, at random | 0.5 | probability | assumption | true | — |
| generator | `txa_benefit_at_zero_delay`: Relative reduction in bleeding death from tranexamic acid given at the moment of injury | 0.41 | relative reduction | assumption | true | — |
| generator | `txa_rr_by_delay`: Relative risk of bleeding death with tranexamic acid, by time from injury to treatment | up_to_1h 0.68, from_1h_to_3h 0.79, over_3h 1.44 | relative risk | E-22 | false | — |
| generator | `txa_benefit_decay`: Decline of the benefit of tranexamic acid with delay | decline_per_15min 0.1, none_after_h 3 | share of the benefit at zero delay; hours | E-24 | false | — |
