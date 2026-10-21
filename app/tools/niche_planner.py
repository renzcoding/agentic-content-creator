
NICHES = {
    "religion": {
        "name": "Religion / Islam",
        "audience": "Muslims seeking practical Islamic knowledge",
        "goal": "Educate and encourage positive religious practice",
        "points": [
            "Explain one Islamic concept clearly",
            "Provide a relevant daily-life example",
            "Give a practical takeaway based on reliable sources",
        ],
        "hook": "Start with a relatable question about daily Muslim life",
        "cta": "Invite viewers to share reflections respectfully",
    },
    "health": {
        "name": "Health",
        "audience": "People seeking beginner-friendly health information",
        "goal": "Share evidence-based health education",
        "points": [
            "Explain one health topic simply",
            "Provide a practical everyday example",
            "Offer a safe takeaway without replacing professional advice",
        ],
        "hook": "Start with a common health concern",
        "cta": "Invite viewers to share healthy habits",
    },
    "tech": {
        "name": "Tech & AI",
        "audience": "Beginners interested in technology and AI",
        "goal": "Make technology easier to understand and use",
        "points": [
            "Explain one technology concept simply",
            "Demonstrate a practical real-world use case",
            "Give an actionable tip viewers can try",
        ],
        "hook": "Start with a common problem AI can help solve",
        "cta": "Ask viewers how they would use this technology",
    },
    "business": {
        "name": "Business & Finance",
        "audience": "Beginners learning business and personal finance",
        "goal": "Build practical business and financial literacy",
        "points": [
            "Explain one business or finance concept",
            "Show a realistic example",
            "Provide a practical takeaway and mention relevant risks",
        ],
        "hook": "Start with a common business or money mistake",
        "cta": "Invite viewers to share their learning experiences",
    },
    "food": {
        "name": "Food & Beverage",
        "audience": "Food lovers and beginner home cooks",
        "goal": "Share useful food ideas and cooking inspiration",
        "points": [
            "Introduce a dish, ingredient, or cooking technique",
            "Explain a practical preparation tip",
            "Give an easy idea viewers can try at home",
        ],
        "hook": "Start with a tempting food result or cooking problem",
        "cta": "Ask viewers which dish they want to see next",
    },
    "sport": {
        "name": "Sports",
        "audience": "Sports fans and beginner athletes",
        "goal": "Inform and engage sports enthusiasts",
        "points": [
            "Explain a sports topic, technique, or development",
            "Provide a concrete example",
            "Share a useful insight or beginner-friendly tip",
        ],
        "hook": "Start with a surprising sports fact or question",
        "cta": "Invite viewers to share their opinions",
    },
    "music": {
        "name": "Music",
        "audience": "Music fans and aspiring musicians",
        "goal": "Entertain and educate music audiences",
        "points": [
            "Introduce a music topic or technique",
            "Explain an interesting detail or example",
            "Share a listening tip or creative takeaway",
        ],
        "hook": "Start with a musical question or surprising fact",
        "cta": "Ask viewers about their favorite music",
    },
    "children": {
        "name": "Children",
        "audience": "Children and families",
        "goal": "Create safe, age-appropriate educational entertainment",
        "points": [
            "Introduce one simple learning concept",
            "Explain it through a friendly example or story",
            "End with a positive, easy activity",
        ],
        "hook": "Start with a playful question or curiosity",
        "cta": "Invite children to learn or try the activity with an adult",
    },
    "muslim_faceless": {
        "name": "Faceless Muslim Content",
        "audience": "Muslim audiences watching short-form faceless videos",
        "goal": "Share meaningful Islamic reminders through visual storytelling",
        "points": [
            "Open with a relatable spiritual reflection",
            "Explain one practical lesson supported by reliable sources",
            "End with a thoughtful daily-life application",
        ],
        "hook": "Start with an emotional but respectful Islamic reflection",
        "cta": "Invite viewers to reflect or share the reminder",
    },
}


def plan_content(topic: str, niche: str = "tech") -> dict:
    """Create a niche-specific content plan."""
    niche_key = niche.strip().lower()

    if niche_key not in NICHES:
        valid_niches = ", ".join(NICHES.keys())
        raise ValueError(f"Unknown niche. Choose one of: {valid_niches}")

    profile = NICHES[niche_key]

    return {
        "topic": topic.strip(),
        "niche": profile["name"],
        "target_audience": profile["audience"],
        "content_goal": profile["goal"],
        "format": "Short-form vertical video",
        "key_points": profile["points"],
        "hook_direction": profile["hook"],
        "cta": profile["cta"],
    }
