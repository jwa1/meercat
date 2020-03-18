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

    def find_equivalent_switch(self, model):
        try:
            db_session = models.Session()
            requested_switch = self.find_switch_by_model(db_session, model)
            if len(requested_switch) == 1:
                mapping_id = self.find_switch_mapping(db_session, requested_switch[0].id)
                equivalent_switch = self.find_switch_by_id(db_session, mapping_id)
                return equivalent_switch
            elif len(requested_switch) == 0:
                return None
            else:
                return requested_switch
        except InvalidRequestError:
            db_session.rollback()

    def find_switch_by_id(self, db_session, id):
        switches = db_session.query(models.Switch) \
                                .filter(models.Switch.id == id) \
                                .all()
        
        return switches

    def find_switch_by_model(self, db_session, model):
        switches = db_session.query(models.Switch) \
                                .filter(models.Switch.model.like(f"%{model}%")) \
                                .all()
        
        return switches

    def find_switch_mapping(self, db_session, id):
        # Meraki models always start with M
        if id[0].lower() == "m":
            matches = db_session.query(models.Mapping) \
                                .filter(models.Mapping.meraki == id) \
                                .all()
            return matches[0].catalyst
        else:
            matches = db_session.query(models.Mapping) \
                                .filter(models.Mapping.catalyst == id) \
                                .all()
            return matches[0].meraki

        if __debug__:
            print(f"Error could not find mapping for {id}")
        return None