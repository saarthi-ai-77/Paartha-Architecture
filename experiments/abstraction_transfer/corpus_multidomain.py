"""
Multi-Domain Task Corpus for Genuine Abstraction Transfer.
Defines three completely independent, non-co-designed domains:
- Domain A: Freight Supply Chain & Fleet Logistics
- Domain B: Molecular Spectroscopy & Cryogenic Telemetry
- Domain C: Financial Market Microstructure & High-Frequency Order Execution

Zero shared column names, entity values, units, or task prompts.
"""

from typing import Dict, List, Tuple, Any
from decisive_paartha.tools.primitive_tools import State, initialize_primitive_tools
from decisive_paartha.benchmark.task_corpus import BenchmarkTask

def run_ideal(steps: List[Tuple[str, Dict[str, Any]]], init_state: State) -> State:
    tools = initialize_primitive_tools()
    s = init_state.clone()
    for name, args in steps:
        s = tools[name].execute(s, args)
    return s

def get_multidomain_corpus() -> Dict[str, List[BenchmarkTask]]:
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
    # DOMAIN B DATA: MOLECULAR SPECTROSCOPY & CRYOGENIC SENSORS
    # ==========================================================================
    spectroscopy_data = [
        {"probe_id": "PR-01", "chamber": "Alpha", "absorbance_nm": 450.0, "temp_kelvin": 14.0, "quantum_noise": 0.012},
        {"probe_id": "PR-02", "chamber": "Beta", "absorbance_nm": 120.0, "temp_kelvin": 8.0, "quantum_noise": 0.045},
        {"probe_id": "PR-03", "chamber": "Alpha", "absorbance_nm": 890.0, "temp_kelvin": 24.0, "quantum_noise": 0.008},
        {"probe_id": "PR-04", "chamber": "Gamma", "absorbance_nm": 310.0, "temp_kelvin": 11.0, "quantum_noise": 0.031},
        {"probe_id": "PR-05", "chamber": "Beta", "absorbance_nm": 670.0, "temp_kelvin": 18.0, "quantum_noise": 0.019},
        {"probe_id": "PR-06", "chamber": "Gamma", "absorbance_nm": 940.0, "temp_kelvin": 28.0, "quantum_noise": 0.005},
        {"probe_id": "PR-07", "chamber": "Alpha", "absorbance_nm": 520.0, "temp_kelvin": 16.0, "quantum_noise": 0.022},
        {"probe_id": "PR-08", "chamber": "Beta", "absorbance_nm": 230.0, "temp_kelvin": 9.0, "quantum_noise": 0.038},
    ]

    # ==========================================================================
    # DOMAIN C DATA: FINANCIAL MARKET MICROSTRUCTURE & ORDER ROUTING
    # ==========================================================================
    finance_data = [
        {"order_id": "ORD-501", "exchange": "BATS", "spread_bps": 4.5, "latency_micros": 140.0, "fill_volume": 12000},
        {"order_id": "ORD-502", "exchange": "ARCA", "spread_bps": 1.2, "latency_micros": 80.0, "fill_volume": 4000},
        {"order_id": "ORD-503", "exchange": "BATS", "spread_bps": 8.9, "latency_micros": 240.0, "fill_volume": 25000},
        {"order_id": "ORD-504", "exchange": "IEX", "spread_bps": 3.1, "latency_micros": 110.0, "fill_volume": 8500},
        {"order_id": "ORD-505", "exchange": "ARCA", "spread_bps": 6.7, "latency_micros": 180.0, "fill_volume": 18000},
        {"order_id": "ORD-506", "exchange": "IEX", "spread_bps": 9.4, "latency_micros": 280.0, "fill_volume": 31000},
        {"order_id": "ORD-507", "exchange": "BATS", "spread_bps": 5.2, "latency_micros": 160.0, "fill_volume": 14000},
        {"order_id": "ORD-508", "exchange": "ARCA", "spread_bps": 2.3, "latency_micros": 90.0, "fill_volume": 6000},
    ]

    # --------------------------------------------------------------------------
    # DOMAIN A EXPERIENCE TASKS (Discovery source)
    # --------------------------------------------------------------------------
    exp_tasks = []
    # EXP 1: FilterByThreshold -> SortByColumn -> TopK
    s1 = [
        ("FilterByThreshold", {"col": "freight_cost", "threshold": 250.0, "operator": ">"}),
        ("SortByColumn", {"col": "transit_hours", "ascending": True}),
        ("TopK", {"k": 3})
    ]
    exp_tasks.append(BenchmarkTask(
        "TASK_A_EXP_01", "Experience", "Domain_A_Logistics",
        "Select shipments costing over 250, sorted by transit duration ascending, take the first 3.",
        State(logistics_data), run_ideal(s1, State(logistics_data)), s1
    ))

    # EXP 2: FilterByThreshold -> SortByColumn -> TopK
    s2 = [
        ("FilterByThreshold", {"col": "weight_kg", "threshold": 1000.0, "operator": ">"}),
        ("SortByColumn", {"col": "freight_cost", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    exp_tasks.append(BenchmarkTask(
        "TASK_A_EXP_02", "Experience", "Domain_A_Logistics",
        "Find heavy cargo with weight exceeding 1000 kg, sorted by freight cost descending, return top 2.",
        State(logistics_data), run_ideal(s2, State(logistics_data)), s2
    ))

    # EXP 3: FilterByThreshold -> SortByColumn
    s3 = [
        ("FilterByThreshold", {"col": "transit_hours", "threshold": 15.0, "operator": "<="}),
        ("SortByColumn", {"col": "weight_kg", "ascending": True})
    ]
    exp_tasks.append(BenchmarkTask(
        "TASK_A_EXP_03", "Experience", "Domain_A_Logistics",
        "Extract shipments with transit hours 15 or less, ordered by cargo weight.",
        State(logistics_data), run_ideal(s3, State(logistics_data)), s3
    ))

    # EXP 4: GroupBy -> AggregateSum -> SortByColumn
    s4 = [
        ("GroupBy", {"group_col": "hub"}),
        ("AggregateSum", {"num_col": "freight_cost", "out_col": "total_cost"}),
        ("SortByColumn", {"col": "total_cost", "ascending": False})
    ]
    exp_tasks.append(BenchmarkTask(
        "TASK_A_EXP_04", "Experience", "Domain_A_Logistics",
        "Calculate total freight expenditures grouped by regional hub, sorted from highest to lowest.",
        State(logistics_data), run_ideal(s4, State(logistics_data)), s4
    ))

    # EXP 5: FilterEquals -> SortByColumn -> TopK
    s5 = [
        ("FilterEquals", {"col": "hub", "val": "North"}),
        ("SortByColumn", {"col": "freight_cost", "ascending": True}),
        ("TopK", {"k": 2})
    ]
    exp_tasks.append(BenchmarkTask(
        "TASK_A_EXP_05", "Experience", "Domain_A_Logistics",
        "Retrieve lowest cost shipments originating from the North hub, take the first 2.",
        State(logistics_data), run_ideal(s5, State(logistics_data)), s5
    ))

    # EXP 6: FilterByThreshold -> SortByColumn -> TopK
    s6 = [
        ("FilterByThreshold", {"col": "freight_cost", "threshold": 500.0, "operator": ">="}),
        ("SortByColumn", {"col": "weight_kg", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    exp_tasks.append(BenchmarkTask(
        "TASK_A_EXP_06", "Experience", "Domain_A_Logistics",
        "Find shipments where freight cost is 500 or more, sorted by weight descending, select top 2.",
        State(logistics_data), run_ideal(s6, State(logistics_data)), s6
    ))

    # --------------------------------------------------------------------------
    # DOMAIN B TASKS (Spectroscopy Transfer)
    # --------------------------------------------------------------------------
    b_tasks = []
    # B1: Structural isomorphism to EXP 1 (FilterByThreshold -> SortByColumn -> TopK)
    b_s1 = [
        ("FilterByThreshold", {"col": "absorbance_nm", "threshold": 300.0, "operator": ">"}),
        ("SortByColumn", {"col": "quantum_noise", "ascending": True}),
        ("TopK", {"k": 3})
    ]
    b_tasks.append(BenchmarkTask(
        "TASK_B_01", "Domain_B_Spectroscopy", "Domain_B_Spectroscopy",
        "Filter optical sensors with absorbance over 300 nm, sorted by quantum noise ascending, keep top 3.",
        State(spectroscopy_data), run_ideal(b_s1, State(spectroscopy_data)), b_s1
    ))

    # B2: Structural isomorphism to EXP 2 (FilterByThreshold -> SortByColumn -> TopK)
    b_s2 = [
        ("FilterByThreshold", {"col": "temp_kelvin", "threshold": 12.0, "operator": ">"}),
        ("SortByColumn", {"col": "absorbance_nm", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    b_tasks.append(BenchmarkTask(
        "TASK_B_02", "Domain_B_Spectroscopy", "Domain_B_Spectroscopy",
        "Identify high-temperature detectors above 12 Kelvin, sorted by absorbance descending, select top 2.",
        State(spectroscopy_data), run_ideal(b_s2, State(spectroscopy_data)), b_s2
    ))

    # B3: Structural isomorphism to EXP 4 (GroupBy -> AggregateSum -> SortByColumn)
    b_s3 = [
        ("GroupBy", {"group_col": "chamber"}),
        ("AggregateSum", {"num_col": "absorbance_nm", "out_col": "total_absorbance"}),
        ("SortByColumn", {"col": "total_absorbance", "ascending": False})
    ]
    b_tasks.append(BenchmarkTask(
        "TASK_B_03", "Domain_B_Spectroscopy", "Domain_B_Spectroscopy",
        "Aggregate cumulative absorbance grouped by vacuum chamber, sorted highest to lowest.",
        State(spectroscopy_data), run_ideal(b_s3, State(spectroscopy_data)), b_s3
    ))

    # --------------------------------------------------------------------------
    # DOMAIN C TASKS (Financial Market Microstructure Transfer)
    # --------------------------------------------------------------------------
    c_tasks = []
    # C1: Structural isomorphism to EXP 1 (FilterByThreshold -> SortByColumn -> TopK)
    c_s1 = [
        ("FilterByThreshold", {"col": "spread_bps", "threshold": 3.0, "operator": ">"}),
        ("SortByColumn", {"col": "latency_micros", "ascending": True}),
        ("TopK", {"k": 3})
    ]
    c_tasks.append(BenchmarkTask(
        "TASK_C_01", "Domain_C_Finance", "Domain_C_Finance",
        "Select market orders with spread exceeding 3 bps, ordered by routing latency ascending, select top 3.",
        State(finance_data), run_ideal(c_s1, State(finance_data)), c_s1
    ))

    # C2: Structural isomorphism to EXP 2 (FilterByThreshold -> SortByColumn -> TopK)
    c_s2 = [
        ("FilterByThreshold", {"col": "fill_volume", "threshold": 10000.0, "operator": ">"}),
        ("SortByColumn", {"col": "spread_bps", "ascending": False}),
        ("TopK", {"k": 2})
    ]
    c_tasks.append(BenchmarkTask(
        "TASK_C_02", "Domain_C_Finance", "Domain_C_Finance",
        "Find large block orders with fill volume exceeding 10000 shares, sorted by spread descending, return top 2.",
        State(finance_data), run_ideal(c_s2, State(finance_data)), c_s2
    ))

    # C3: Structural isomorphism to EXP 4 (GroupBy -> AggregateSum -> SortByColumn)
    c_s3 = [
        ("GroupBy", {"group_col": "exchange"}),
        ("AggregateSum", {"num_col": "fill_volume", "out_col": "total_volume"}),
        ("SortByColumn", {"col": "total_volume", "ascending": False})
    ]
    c_tasks.append(BenchmarkTask(
        "TASK_C_03", "Domain_C_Finance", "Domain_C_Finance",
        "Compute total execution volume grouped by electronic exchange venue, ranked from largest to smallest volume.",
        State(finance_data), run_ideal(c_s3, State(finance_data)), c_s3
    ))

    return {
        "domain_a_experience": exp_tasks,
        "domain_b_spectroscopy": b_tasks,
        "domain_c_finance": c_tasks
    }
