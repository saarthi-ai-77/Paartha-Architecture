"""
Lesson Parsing & Construction Engine (KRS-001 / ACA-0)

Transforms natural language instructional text into KRS-001 computational knowledge graph structures.
"""

from krs import InvariantRule

def clean_symbol(s):
    s = s.strip().rstrip(".")
    lower = s.lower()
    if lower.endswith("uses"):
        s = s[:-2]  # Platypuses -> Platypus
    elif lower.endswith("es") and not lower.endswith("o") and not lower.endswith("s"):
        s = s[:-1]
    elif lower.endswith("s") and not lower.endswith("ss") and not lower.endswith("is") and len(lower) > 3:
        s = s[:-1]  # Whales -> Whale, Mammals -> Mammal, Dolphins -> Dolphin
    return s.capitalize()

class LessonParser:
    def __init__(self):
        pass

    def parse_and_construct(self, text_lines, kg):
        constructed_elements = []
        for line in text_lines:
            line_str = line.strip()
            if not line_str: continue

            # Pattern 1: Universal rule "All X breathe Y" / "All X <pred> Y"
            if line_str.startswith("All ") and " breathe " in line_str:
                parts = line_str[len("All "):].split(" breathe ")
                cond_target = clean_symbol(parts[0])
                impl_target = clean_symbol(parts[1])
                rule = InvariantRule(
                    rule_id=f"Rule_{cond_target}_{impl_target}",
                    cond_pred="is_a",
                    cond_target=cond_target,
                    impl_pred="breathes",
                    impl_target=impl_target
                )
                kg.add_invariant(rule)
                constructed_elements.append(rule)

            # Pattern 2: Subclass fact "X are Y" / "X is a Y"
            elif " are " in line_str or " is a " in line_str or " were " in line_str:
                if " are " in line_str:
                    subj, obj = line_str.split(" are ")
                elif " is a " in line_str:
                    subj, obj = line_str.split(" is a ")
                else:
                    subj, obj = line_str.split(" were ")

                subj_clean = clean_symbol(subj)
                obj_clean = clean_symbol(obj)

                edge = kg.add_relation(subj_clean, "is_a", obj_clean)
                constructed_elements.append(edge)

            # Pattern 3: Explicit conclusion "Therefore X breathe Y"
            elif line_str.startswith("Therefore ") and " breathe " in line_str:
                parts = line_str[len("Therefore "):].split(" breathe ")
                subj_clean = clean_symbol(parts[0])
                obj_clean = clean_symbol(parts[1])
                edge = kg.add_relation(subj_clean, "breathes", obj_clean)
                constructed_elements.append(edge)

        return constructed_elements
