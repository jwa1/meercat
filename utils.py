from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.components import TextBlock, Fact, Column, Image, ImageSize
from pyadaptivecards.container import FactSet, Container

def generate_adaptive_card(original_model, switch_data):
    title = Container(items=[
        TextBlock(text=f"The {original_model} is equivalent to the", size="Small", weight="Lighter"),
        TextBlock(text=f"{switch_data.model}", size="ExtraLarge", color="Accent", spacing=None)
    ])

    facts = []
    for attr, value in vars(switch_data).items():
        # Don't append null values or internal attributes
        if value and value != 'null' and attr[0] != '_':
            facts.append(Fact(attr, value))
    factset = FactSet(facts)

    card = AdaptiveCard(body=[title, factset])

    attachment = {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": card.to_dict(),
    }

    return attachment
