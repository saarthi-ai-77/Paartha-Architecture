"""
Class-C explicit stubs (SIP-001 Section 1) -- open hypotheses this program
has not validated. Real interfaces, no invented logic behind them. Per the
directive that produced SIP-001: "design the runtime so each [open
question] can later be investigated independently... Do not merge them
into implementation."
"""


def generate_curriculum(learning_opportunities, episode_log=None):
    """Offline Mentor Curriculum (SIP-001 Section 2, row 14). Status:
    docs/05_research/proposals/developmental_mentor_paradigm.md --
    "Requires Prerequisite Research," EXP-008 not run. Explicit no-op."""
    return {
        "status": "not_implemented",
        "reason": "mentor-society proposal status: Requires Prerequisite Research (EXP-008 not run)",
        "n_learning_opportunities_pending": len(learning_opportunities),
    }


def discover_family(observed_examples):
    """RC-02 automatic family/structure discovery (SIP-001 Section 17,
    EXP-005). Explicit no-op -- EXP-020's compose module requires a hand-
    verified grammar; this stub marks where a discovery mechanism would
    plug in without touching compose.py's interpreter."""
    return {
        "status": "not_implemented",
        "reason": "EXP-005 not run -- structure discovery remains the central open problem since EXP-002",
    }


def learned_route(request_features):
    """RC-02 learned routing (SIP-001 Section 2, row 7 dispatch
    alternative). Explicit no-op -- this runtime uses fixed, non-learned
    routing exclusively, per EXP-004/EXP-021's validated design."""
    return {
        "status": "not_implemented",
        "reason": "RC-02 learned routing unimplemented per ACA v1.0 Section 8; fixed routing used instead",
    }
