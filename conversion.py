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

            # Construct a filter based on current information
            filters = []
            if model:
                # TODO: Move this somewhere better
                model = model.replace("-", "%-%")
                filters.append(models.Switch.model.like(f"%{model}%"))
            if network_module:
                # TODO: Move this somewhere better
                network_module = network_module.replace("-", "%-%")
                filters.append(models.Switch.network_module.like(f"%{network_module}%"))

            requested_switch = self.find_switches_with_filters(db_session, filters)

            # We found one match
            if len(requested_switch) == 1:
                mapping_id = self.find_switch_mapping(db_session, requested_switch[0].id)
                # Could not find an equivalent
                if not mapping_id:
                    data["matched"] = True
                    return data
                equivalent_switch = self.find_switch_by_id(db_session, mapping_id)
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

    def find_switches_with_filters(self, db_session, filters):
        switches = db_session.query(models.Switch)

        for filter in filters:
            switches = switches.filter(filter)
        
        return switches.all()

    def find_switch_by_id(self, db_session, id):
        return db_session.query(models.Switch).filter(models.Switch.id.like(f"%{id}%")).all()

    def find_switch_by_model(self, db_session, model, fuzzy_match=False):
        # To fuzzy match we will inlude wildcards in between each model break
        # E.g. C9300L-48T-4G-E -> %C9300L%-%48T%-%4G%-%E%
        # This will ensure that C9300L-48T will match switches in that family
        if fuzzy_match:
            model = model.replace("-", "%-%")

        return self.find_switches_with_filters(
                    db_session,
                    models.Switch.model.like(f"%{model}%"),
                )

    def find_switch_mapping(self, db_session, id):
        # Meraki models always start with M
        if id[0].lower() == "m":
            matches = db_session.query(models.Mapping).filter(
                            models.Mapping.meraki.like(f"%{id}%")
                        ).all()
            if matches:
                return matches[0].catalyst
        else:
            matches = db_session.query(models.Mapping).filter(
                            models.Mapping.catalyst.like(f"%{id}%")
                        ).all()
            if matches:
                return matches[0].meraki

        if __debug__:
            print(f"Error could not find mapping for {id}")
        return None