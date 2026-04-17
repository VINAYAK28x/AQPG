"""
Question generation constants — Bloom's taxonomy verbs, stopwords, valid openers,
and the Ollama scaffold template.

Extracted from question_service.py to keep the service file focused on orchestration.
"""

# =====================================================
# Bloom's Taxonomy Verb Map (Step 4 from upgrade plan)
# =====================================================
BLOOM_VERBS = {
    "Remember": ["define", "list", "identify"],
    "Understand": ["explain", "summarize"],
    "Apply": ["solve", "demonstrate"],
    "Analyze": ["compare", "differentiate"],
    "Evaluate": ["justify", "critique"],
    "Create": ["design", "formulate"],
}

GENERIC_SUBJECT_NAMES = {"", "unknown", "computer science"}

CONTEXT_STOPWORDS = {
    "about", "after", "again", "against", "algorithm", "algorithms", "also", "among",
    "and", "another", "apply", "approach", "approaches", "architecture", "because",
    "before", "between", "both", "can", "concept", "concepts", "consider", "course",
    "data", "define", "describe", "design", "detail", "different", "discuss", "each",
    "effect", "effects", "example", "examples", "explain", "feature", "features",
    "following", "from", "function", "functions", "how", "important", "importance",
    "include", "including", "into", "level", "marks", "module", "more", "most",
    "nature", "operating", "operation", "operations", "provide", "question", "real",
    "related", "role", "state", "system", "systems", "their", "these", "this",
    "through", "topic", "used", "using", "what", "when", "where", "which", "with",
}

VALID_OPENERS = {
    # Bloom's L1 – Remember
    "define", "state", "list", "name", "identify", "recall",
    "recognise", "recognize", "label", "select", "match",
    "outline", "enumerate", "mention", "specify", "reproduce",
    # Bloom's L2 – Understand
    "explain", "describe", "discuss", "summarise", "summarize",
    "interpret", "classify", "distinguish", "paraphrase",
    "illustrate", "clarify", "elaborate", "give", "provide",
    "differentiate", "justify", "represent", "translate",
    # Bloom's L3 – Apply
    "apply", "calculate", "compute", "solve", "determine",
    "find", "derive", "show", "demonstrate", "use",
    "implement", "execute", "construct", "sketch", "draw",
    "plot", "trace", "build", "develop", "formulate",
    "write", "obtain", "verify", "prove", "establish",
    # Bloom's L4 – Analyze
    "analyze", "analyse", "compare", "contrast", "examine",
    "inspect", "investigate", "differentiate", "distinguish",
    "separate", "categorize", "categorise", "deconstruct",
    "deduce", "infer", "relate", "correlate", "break",
    # Bloom's L5 – Evaluate
    "evaluate", "assess", "justify", "judge", "critique",
    "criticise", "criticize", "appraise", "argue", "defend",
    "support", "recommend", "prioritize", "prioritise", "rank",
    "rate", "validate", "review",
    # Bloom's L6 – Create
    "design", "propose", "create", "develop", "plan",
    "formulate", "devise", "generate", "compose", "produce",
    "synthesize", "synthesise", "construct", "assemble", "modify",
    # Interrogatives
    "what", "how", "why", "when", "where", "which", "who",
    "whom", "whose", "is", "are", "does", "do", "can",
    "could", "should", "would", "will", "may", "might",
    # Math / Engineering starters
    "consider", "suppose", "assume", "given", "let",
    "if", "for", "using", "with", "perform",
    "simulate", "model", "estimate", "approximate", "convert",
    "transform", "encode", "decode", "encrypt", "decrypt",
    "reduce", "simplify", "minimize", "maximize", "optimize",
    # General academic
    "briefly", "clearly", "critically", "concisely",
    "diagrammatically", "graphically", "mathematically",
    "systematically", "tabulate", "enlist", "highlight",
    "point", "note", "comment", "remark", "suggest",
    "express", "present", "depict", "map", "arrange",
}

SCAFFOLD_TEMPLATE = """\
You generate clean university exam questions from syllabus metadata and context.

### Instruction:
Create one appropriate exam question from the given academic prompt.

### Input:
Subject: {subject}
Module: {module}
Marks: {marks}
Bloom Level: {bloom_level}

{pyq_section}

Context:
{compressed_context}

Construct a relevant question for assessment about '{topic}' based on the context.

### Response:
"""
