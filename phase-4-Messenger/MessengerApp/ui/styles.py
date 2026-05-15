def get_theme(theme="dark"):
    dark = theme == "dark"

    return {
        "window": "#0E0F14" if dark else "#F8F5FF",
        "panel": "#0E0F14" if dark else "#FFFDFE",
        "panel_2": "#12131A" if dark else "#FBF7FF",
        "panel_3": "#090A0E" if dark else "#F7F0FF",
        "card": "#1A1B26" if dark else "#F1E6FF",
        "card_2": "#1A1C23" if dark else "#FFFFFF",
        "border": "#1A1C23" if dark else "#E5D6F6",
        "text": "white" if dark else "#211A2E",
        "muted": "#A0A1B2" if dark else "#77688F",
        "muted_2": "#5A5B6A" if dark else "#A396B8",
        "input": "#181A20" if dark else "#FFFFFF",
        "hover": "#252636" if dark else "#F3E9FF",
        "bubble_other": "#1A1C23" if dark else "#FFFFFF",
        "promo_1": "#1A153A" if dark else "#F8EEFF",
        "promo_2": "#0F0A20" if dark else "#F1E7FF",
    }