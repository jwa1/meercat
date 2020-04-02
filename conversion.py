import dialogflow
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

import models
from sqlalchemy.exc import InvalidRequestError

class Converter:
    def __init__(self, project_id, session_id):
        super().__init__()
        self.project_id = project_id
        self.df_session_client = dialogflow.SessionsClient()

    def detect_intent_texts(self, session_id, text, language_code):
        if text:
            df_session = self.df_session_client.session_path(self.project_id, session_id)

            text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
            query_input = dialogflow.types.QueryInput(text=text_input)

            response = self.df_session_client.detect_intent(session=df_session, query_input=query_input)

            return response.query_result

    def find_equivalent_switch(self, fields):
        try:
            model = fields.get("Model", None)
            network_module = fields.get("Network_Module", None)
            platform = fields.get("Platform", None)

            data = {}
            data["matched"] = False
            data["modular"] = False
            data["switches"] = []

            db_session = models.Session()

            requested_switch = self.find_switches_with_filters(db_session, 
                                    model=model, 
                                    network_module=network_module
                                )

            # We found one match
            if len(requested_switch) == 1:
                mapping_ids = self.find_switch_mapping(db_session, requested_switch[0].id)
                # Could not find an equivalent
                if not mapping_ids:
                    data["matched"] = True
                    return data
                equivalent_switch = []
                for mapping_id in mapping_ids:
                    matches = self.find_switch_by_id(db_session, mapping_id)
                    if len(matches) == 0:
                        matches.extend(self.find_switch_by_id(db_session, mapping_id, expand=True))
                    equivalent_switch.extend(matches)
                    # Pass the data back
                data["switches"] = equivalent_switch
                data["matched"] = True
            # Did not find any matching switch
            elif not requested_switch:
                return data
            # Multiple results, not fully matched yet
            else:
                data["switches"] = requested_switch
                data["matched"] = False
            
            # Check if the switch is modular
            if len(requested_switch) > 1:
                data["modular"] = requested_switch[0].modular
            return data
                
        except InvalidRequestError:
            # An SQL error will occur if the database is being spammed
            db_session.rollback()
            return data

        finally:
            db_session.close()

    # To fuzzy match we will inlude wildcards in between each model break
    # E.g. C9300L-48T-4G-E -> %C9300L%-%48T%-%4G%-%E%
    # This will ensure that C9300L-48T will match switches in that family
    def find_switches_with_filters(self, db_session, fuzzy_match=False, expand=True, id=None, model=None, network_module=None, add_meraki_hw_suffix=False):
        switches = db_session.query(models.Switch)

        # Filter based on passed parameters
        if model and model != '':
            if add_meraki_hw_suffix and not model.lower().endswith("hw"):
                model = model + "-HW"
            if fuzzy_match:
                model = '%' + model.replace("-", "%-%") + '%'
            switches = switches.filter(models.Switch.model.like(f"{model}"))
        if network_module and network_module != '':
            if fuzzy_match:
                network_module = '%' + network_module.replace("-", "%-%") + '%'
            switches = switches.filter(models.Switch.network_module.like(f"{network_module}"))
        if id and id != '':
            if fuzzy_match:
                id = '%' + id.replace("-", "%-%") + '%'
            switches = switches.filter(models.Switch.id.like(f"{id}"))

        # Get all switches from the query
        switches = switches.all()

        # Do a recursive fuzzy match if a direct match wasn't found
        # Do a recursive fuzzy match if a direct match wasn't found
        if len(switches) == 0 and not add_meraki_hw_suffix and expand:
            return self.find_switches_with_filters(db_session,
                        fuzzy_match=fuzzy_match,
                        model=model,
                        network_module=network_module,
                        id=id,
                        add_meraki_hw_suffix=True
                    )
        if len(switches) == 0 and not fuzzy_match and expand:
            return self.find_switches_with_filters(db_session,
                        fuzzy_match=True,
                        model=model,
                        network_module=network_module,
                        id=id,
                        add_meraki_hw_suffix=add_meraki_hw_suffix
                    )

        return switches

    def find_switch_by_id(self, db_session, id, expand=False):
        return self.find_switches_with_filters(db_session, id=id, expand=expand)

    def find_switch_by_model(self, db_session, model, expand=True):
        return self.find_switches_with_filters(db_session, model=model, expand=expand)

    def find_switch_mapping(self, db_session, id):
        # Meraki models always start with M
        if id[0].lower() == "m":
            matches = db_session.query(models.Mapping).filter(
                            models.Mapping.meraki.like(f"%{id}%")
                        ).all()
            if matches:
                return [m.catalyst for m in matches]
                # return matches[0].catalyst
        else:
            matches = db_session.query(models.Mapping).filter(
                            models.Mapping.catalyst.like(f"%{id}%")
                        ).all()
            if matches:
                return [m.meraki for m in matches]

        if __debug__:
            print(f"Error could not find mapping for {id}")
        return None