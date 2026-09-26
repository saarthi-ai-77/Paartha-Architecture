"""
Task Corpus Generator for Paartha Decisive Experiment.
Defines:
- Experience Corpus (Domain A: Supply Chain Logistics)
- Level 1: Familiar compositions (Domain A)
- Level 2: Held-out compositions (Domain A)
- Level 3: Independently authored cross-domain transfer (Domain B: Spectroscopy & Sensor Telemetry)
"""

import copy
from typing import Dict, List, Tuple, Any, Optional

from decisive_paartha.tools.primitive_tools import (
    State, Capability, StepAST, ProgramAST, initialize_primitive_tools
)

class BenchmarkTask:
    def __init__(
        self,
        task_id: str,
        level: str, # "Level_1_Familiar", "Level_2_HeldOut", "Level_3_Transfer"
        domain: str, # "Domain_A_Logistics", "Domain_B_Spectroscopy"
        description: str,
        initial_state: State,
        expected_state: State,
        ideal_steps: List[Tuple[str, Dict[str, Any]]]
    ):
        self.task_id = task_id
        self.level = level
        self.domain = domain
        self.description = description
        self.initial_state = initial_state
        self.expected_state = expected_state
        self.ideal_steps = ideal_steps


def get_benchmark_corpus() -> Dict[str, List[BenchmarkTask]]:
    primitives = initialize_primitive_tools()

    # ==========================================================================
    # DOMAIN A DATA: LOGISTICS & SUPPLY CHAIN
    # ==========================================================================
    logistics_data = [
        {"shipment_id": "SH-101", "hub": "Central", "freight_cost": 450.0, "transit_hours": 14, "weight_kg": 1200},
        {"shipment_id": "SH-102", "hub": "North", "freight_cost": 120.0, "transit_hours": 8, "weight_kg": 400},
        {"shipment_id": "SH-103", "hub": "Central", "freight_cost": 890.0, "transit_hours": 24, "weight_kg": 2500},
        {"shipment_id": "SH-104", "hub": "South", "freight_cost": 310.0, "transit_hours": 11, "weight_kg": 850},
        {"shipment_id": "SH-105", "hub": "North", "freight_cost": 670.0, "transit_hours": 18, "weight_kg": 1800},
        {"shipment_id": "SH-106", "hub": "South", "freight_cost": 940.0, "transit_hours": 28, "weight_kg": 3100},
        {"shipment_id": "SH-107", "hub": "Central", "freight_cost": 520.0, "transit_hours": 16, "weight_kg": 1400},
        {"shipment_id": "SH-108", "hub": "North", "freight_cost": 230.0, "transit_hours": 9, "weight_kg": 600},
    ]

    # ==========================================================================
    # DOMAIN B DATA: MOLECULAR SPECTROSCOPY & SENSOR TELEMETRY (HELD-OUT TRANSFER)
    # Zero shared entities, column names, units, or vocabulary with Domain A.
    # ==========================================================================
    spectroscopy_data = [
        {"probe_id": "PR-01", "chamber": "Alpha", "absorbance_nm": 450.0, "temp_kelvin": 14.0, "quantum_noise": 0.012},
        {"probe_id": "PR-02", "chamber": "Beta", "absorbance_nm": 120.0, "temp_kelvin": 8.0, "quantum_noise": 0.045},
        {"probe_id": "PR-03", "chamber": "Alpha", "absorbance_nm": 890.0, "temp_kelvin": 24.0, "quantum_noise": 0.008},
        {"probe_id": "PR-04", "chamber": "Gamma", "absorbance_nm": 310.0, "temp_kelvin": 11.0, "quantum_noise": 0.033},
        {"probe_id": "PR-05", "chamber": "Beta", "absorbance_nm": 670.0, "temp_kelvin": 18.0, "quantum_noise": 0.019},
        {"probe_id": "PR-06", "chamber": "Gamma", "absorbance_nm": 940.0, "temp_kelvin": 28.0, "quantum_noise": 0.005},
        {"probe_id": "PR-07", "chamber": "Alpha", "absorbance_nm": 520.0, "temp_kelvin": 16.0, "quantum_noise": 0.015},
        {"probe_id": "PR-08", "chamber": "Beta", "absorbance_nm": 230.0, "temp_kelvin": 9.0, "quantum_noise": 0.038},
    ]

    def run_ideal(steps: List[Tuple[str, Dict[str, Any]]], init_s: State) -> State:
        curr = init_s.clone()
        for name, args in steps:
            curr = primitives[name].execute(curr, args)
        return curr

    # --------------------------------------------------------------------------
    # 1. EXPERIENCE TASKS (Domain A - used to seed System D experience phase)
    # Recurring Motif 1: FilterByThreshold -> SortByColumn -> TopK
    # Recurring Motif 2: GroupBy -> AggregateSum -> SortByColumn
    # --------------------------------------------------------------------------
    experience_tasks = []

    # EXP_1: Filter freight_cost > 300, sort descending, top 3
    s1 = [
        ("FilterByThreshold", {"col": "freight_cost", "threshold": 300.0, "operator": ">"}),
        ("SortByColumn", {"col": "freight_cost", "ascending": False}),
        ("TopK", {"k": 3})
    ]
    experience_tasks.append(BenchmarkTask(
        "T_EXP_01", "Experience", "Domain_A_Logistics",
        "Retrieve the top 3 highest freight cost shipments above 300 USD.",
        State(logistics_data), run_ideal(s1, State(logistics_data)), s1
    ))

    # EXP_2: Filter transit_hours > 10, sort descending, top 2
    s2 = [
        ("FilterByThreshold", {"col": "transit_hours", "threshold": 10.0, "operator": ">"}),
        ("SortByColumn", {"col": "transit_hours", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    experience_tasks.append(BenchmarkTask(
        "T_EXP_02", "Experience", "Domain_A_Logistics",
        "Identify the top 2 longest transit shipments with transit hours above 10.",
        State(logistics_data), run_ideal(s2, State(logistics_data)), s2
    ))

    # EXP_3: Group by hub, Aggregate freight_cost sum, sort descending
    s3 = [
        ("GroupBy", {"group_col": "hub"}),
        ("AggregateSum", {"num_col": "freight_cost", "out_col": "total_freight"}),
        ("SortByColumn", {"col": "total_freight", "ascending": False})
    ]
    experience_tasks.append(BenchmarkTask(
        "T_EXP_03", "Experience", "Domain_A_Logistics",
        "Calculate total freight cost by logistics hub sorted from highest to lowest.",
        State(logistics_data), run_ideal(s3, State(logistics_data)), s3
    ))

    # EXP_4: Group by hub, Aggregate weight_kg sum, sort descending
    s4 = [
        ("GroupBy", {"group_col": "hub"}),
        ("AggregateSum", {"num_col": "weight_kg", "out_col": "total_weight"}),
        ("SortByColumn", {"col": "total_weight", "ascending": False})
    ]
    experience_tasks.append(BenchmarkTask(
        "T_EXP_04", "Experience", "Domain_A_Logistics",
        "Aggregate total weight cargo grouped by hub and rank descending.",
        State(logistics_data), run_ideal(s4, State(logistics_data)), s4
    ))

    # EXP_5: Filter weight_kg > 500, sort descending, top 4 (3rd instance of Motif 1)
    s5 = [
        ("FilterByThreshold", {"col": "weight_kg", "threshold": 500.0, "operator": ">"}),
        ("SortByColumn", {"col": "weight_kg", "ascending": False}),
        ("TopK", {"k": 4})
    ]
    experience_tasks.append(BenchmarkTask(
        "T_EXP_05", "Experience", "Domain_A_Logistics",
        "Filter shipments weighing above 500 kg, sorted by weight descending, top 4 records.",
        State(logistics_data), run_ideal(s5, State(logistics_data)), s5
    ))

    # EXP_6: Group by hub, Aggregate freight_cost sum, sort descending (3rd instance of Motif 2)
    s6 = [
        ("GroupBy", {"group_col": "hub"}),
        ("AggregateSum", {"num_col": "freight_cost", "out_col": "total_freight"}),
        ("SortByColumn", {"col": "total_freight", "ascending": False})
    ]
    experience_tasks.append(BenchmarkTask(
        "T_EXP_06", "Experience", "Domain_A_Logistics",
        "Group cargo by hub, sum total freight cost, and order hubs descending.",
        State(logistics_data), run_ideal(s6, State(logistics_data)), s6
    ))

    # --------------------------------------------------------------------------
    # 2. LEVEL 1: FAMILIAR COMPOSITION TASKS (Sanity / Calibration)
    # --------------------------------------------------------------------------
    level1_tasks = []

    # L1_1: Filter hub == Central, Sort by transit_hours ascending
    l1_s1 = [
        ("FilterEquals", {"col": "hub", "val": "Central"}),
        ("SortByColumn", {"col": "transit_hours", "ascending": True})
    ]
    level1_tasks.append(BenchmarkTask(
        "TASK_L1_01", "Level_1_Familiar", "Domain_A_Logistics",
        "List all Central hub shipments ordered by ascending transit hours.",
        State(logistics_data), run_ideal(l1_s1, State(logistics_data)), l1_s1
    ))

    # L1_2: Sort by freight_cost ascending, take Top 4
    l1_s2 = [
        ("SortByColumn", {"col": "freight_cost", "ascending": True}),
        ("TopK", {"k": 4})
    ]
    level1_tasks.append(BenchmarkTask(
        "TASK_L1_02", "Level_1_Familiar", "Domain_A_Logistics",
        "Find the 4 most economical shipments with lowest freight cost.",
        State(logistics_data), run_ideal(l1_s2, State(logistics_data)), l1_s2
    ))

    # --------------------------------------------------------------------------
    # 3. LEVEL 2: HELD-OUT UNFAMILIAR COMPOSITIONS (Domain A)
    # --------------------------------------------------------------------------
    level2_tasks = []

    # L2_1: Deduplicate by hub, Scale freight_cost by 1.15, filter > 500, take Top 2
    l2_s1 = [
        ("Deduplicate", {"key_col": "hub"}),
        ("ScaleColumn", {"col": "freight_cost", "factor": 1.15}),
        ("FilterByThreshold", {"col": "freight_cost", "threshold": 500.0, "operator": ">"}),
        ("SortByColumn", {"col": "freight_cost", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    level2_tasks.append(BenchmarkTask(
        "TASK_L2_01", "Level_2_HeldOut", "Domain_A_Logistics",
        "Deduplicate by hub, apply 1.15 fuel surcharge multiplier to freight cost, and find top 2 shipments exceeding 500 USD.",
        State(logistics_data), run_ideal(l2_s1, State(logistics_data)), l2_s1
    ))

    # L2_2: Group by hub, Mean of transit_hours, sort descending, Top 2
    l2_s2 = [
        ("GroupBy", {"group_col": "hub"}),
        ("AggregateMean", {"num_col": "transit_hours", "out_col": "avg_transit"}),
        ("SortByColumn", {"col": "avg_transit", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    level2_tasks.append(BenchmarkTask(
        "TASK_L2_02", "Level_2_HeldOut", "Domain_A_Logistics",
        "Determine the top 2 hubs with the highest average transit hours per shipment.",
        State(logistics_data), run_ideal(l2_s2, State(logistics_data)), l2_s2
    ))

    # L2_3: Filter weight_kg > 1000, sort descending, top 3 (Tests transfer of M1 in same domain)
    l2_s3 = [
        ("FilterByThreshold", {"col": "weight_kg", "threshold": 1000.0, "operator": ">"}),
        ("SortByColumn", {"col": "weight_kg", "ascending": False}),
        ("TopK", {"k": 3})
    ]
    level2_tasks.append(BenchmarkTask(
        "TASK_L2_03", "Level_2_HeldOut", "Domain_A_Logistics",
        "Extract the top 3 heaviest freight shipments with cargo weight over 1000 kg.",
        State(logistics_data), run_ideal(l2_s3, State(logistics_data)), l2_s3
    ))

    # --------------------------------------------------------------------------
    # 4. LEVEL 3: INDEPENDENTLY AUTHORED CROSS-DOMAIN TRANSFER (Domain B: Spectroscopy)
    # The Decisive Test: tests whether abstractions M1 & M2 transfer across domain boundaries.
    # --------------------------------------------------------------------------
    level3_tasks = []

    # L3_1: Filter absorbance_nm > 400.0, sort descending, top 3 (Matches M1 structure on novel scientific schema)
    l3_s1 = [
        ("FilterByThreshold", {"col": "absorbance_nm", "threshold": 400.0, "operator": ">"}),
        ("SortByColumn", {"col": "absorbance_nm", "ascending": False}),
        ("TopK", {"k": 3})
    ]
    level3_tasks.append(BenchmarkTask(
        "TASK_L3_01_TRANSFER", "Level_3_Transfer", "Domain_B_Spectroscopy",
        "Filter sensor telemetry for optical absorbance exceeding 400 nanometers and rank the top 3 highest intensity optical probes.",
        State(spectroscopy_data), run_ideal(l3_s1, State(spectroscopy_data)), l3_s1
    ))

    # L3_2: Filter temp_kelvin > 10.0, sort descending, top 2 (Matches M1 structure on temperature sensor)
    l3_s2 = [
        ("FilterByThreshold", {"col": "temp_kelvin", "threshold": 10.0, "operator": ">"}),
        ("SortByColumn", {"col": "temp_kelvin", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    level3_tasks.append(BenchmarkTask(
        "TASK_L3_02_TRANSFER", "Level_3_Transfer", "Domain_B_Spectroscopy",
        "Identify the top 2 thermal probes operating above cryogenic threshold 10 Kelvin.",
        State(spectroscopy_data), run_ideal(l3_s2, State(spectroscopy_data)), l3_s2
    ))

    # L3_3: Group by chamber, Aggregate absorbance_nm sum, sort descending (Matches M2 structure on chamber partitions)
    l3_s3 = [
        ("GroupBy", {"group_col": "chamber"}),
        ("AggregateSum", {"num_col": "absorbance_nm", "out_col": "total_absorbance"}),
        ("SortByColumn", {"col": "total_absorbance", "ascending": False})
    ]
    level3_tasks.append(BenchmarkTask(
        "TASK_L3_03_TRANSFER", "Level_3_Transfer", "Domain_B_Spectroscopy",
        "Compute cumulative optical absorbance grouped by experimental vacuum chamber, ranked from highest to lowest.",
        State(spectroscopy_data), run_ideal(l3_s3, State(spectroscopy_data)), l3_s3
    ))

    return {
        "experience": experience_tasks,
        "level1": level1_tasks,
        "level2": level2_tasks,
        "level3_transfer": level3_tasks
    }
