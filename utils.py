from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.components import TextBlock, Fact, Column, Image, ImageSize
from pyadaptivecards.container import FactSet, Container
from pyadaptivecards.inputs import Text, Number, Toggle, Choices
from pyadaptivecards.actions import Submit

class Responses:
    @staticmethod
    def generate_model_response(original_model, switch_data):
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

        card = AdaptiveCard(body=[title, factset], fallbackText=str(switch_data))

        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card.to_dict(),
        }

        return attachment

    @staticmethod
    def generate_switches_response(switches):
        response = f"**The following {len(switches)} switches are in the database:**\n\n"

        for switch in switches:
            response += f"- {switch.id}  \n"

        return response.strip()

    @staticmethod
    def generate_mapping_response(mappings):
        response = f"**The following {len(mappings)} mappings are in the database:**\n\n"

        for mapping in mappings:
            response += f"- {mapping.catalyst} <=> {mapping.meraki}  \n"

        return response.strip()

    @staticmethod
    def generate_edit_response(switch):
        title = Container(items=[
            TextBlock(text=f"Currently editing switch", size="Small", weight="Lighter"),
            TextBlock(text=f"{switch.model}", size="ExtraLarge", color="Accent", spacing=None)
        ])

        items = []
        for attr, value in vars(switch).items():
            # Don't append null values or internal attributes
            if value and value != 'null' and attr[0] != '_':
                if type(value) == bool:
                    items.append(
                        Toggle(attr, attr, value=value)
                    )
                else:
                    items.append(
                        TextBlock(text=f"{attr}")
                    )
                    items.append(
                        Text(attr, placeholder=f"{attr}", value=value)
                    )
                
        submit = Submit(title="Update")

        body = Container(items=items)

        card = AdaptiveCard(body=[title, body], actions=[submit], fallbackText=str(switch))

        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card.to_dict(),
        }

        return attachment