import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

import models
from sqlalchemy.exc import InvalidRequestError

class Editor():
    def __init__(self):
        pass

    def can_user_edit(self, person_id, db_session=None):
        # Reuse an existing session if it is passed
        if db_session:
            user = db_session.query(models.User).filter(
                models.User.id == person_id
            ).all()

            if len(user) == 1:
                return user[0].can_edit()
            return False

        # Create a new db session
        else:
            try:
                db_session = models.Session()

                user = db_session.query(models.User).filter(
                    models.User.id == person_id
                ).all()

                if len(user) == 1:
                    return user[0].can_edit()
                return False

            except InvalidRequestError:
                # An SQL error will occur if the database is being spammed
                db_session.rollback()
                return False

            finally:
                db_session.close()

    def allow_user_by_id(self, me, person_id):
        try:
            db_session = models.Session()

            if not self.can_user_edit(me, db_session=db_session):
                return f"You do not have permissions to edit allowed users."

            user = db_session.query(models.User).filter(
                models.User.id == person_id
            ).all()

            if len(user) == 1:
                db_session.remove(user[0])
            
            new_user = models.User(id=person_id, privilege="editor")
            db_session.add(new_user)

            db_session.commit()

            return f"Successfully added {person_id} to the allowed editors list."

        except InvalidRequestError:
            # An SQL error will occur if the database is being spammed
            db_session.rollback()
            return f"Encountered an error please try again later."

        finally:
            db_session.close()

    def disallow_user_by_id(self, me, person_id):
        try:
            db_session = models.Session()

            if not self.can_user_edit(me, db_session=db_session):
                return f"You do not have permissions to edit allowed users."

            user = db_session.query(models.User).filter(
                models.User.id == person_id
            ).all()

            if len(user) == 1:
                if not user[0].can_edit():
                    return f"User {person_id} is not on the editors list."
                if user[0].is_admin():
                    return f"User {person_id} is an admin and cannot be removed."
                db_session.delete(user[0])
                db_session.commit()
                return f"Successfully removed {person_id} from the allowed editors list."

            return f"User {person_id} is not on the editors list."

        except InvalidRequestError:
            # An SQL error will occur if the database is being spammed
            db_session.rollback()
            return f"Encountered an error please try again later."

        finally:
            db_session.close()

    def list_all_switches(self):
        try:
            db_session = models.Session()

            switches = db_session.query(models.Switch).all()

            return switches

        except InvalidRequestError:
            # An SQL error will occur if the database is being spammed
            db_session.rollback()
            return f"Encountered an error please try again later."

        finally:
            db_session.close()

    def list_all_mapping(self):
        try:
            db_session = models.Session()

            mapping = db_session.query(models.Mapping).all()

            return mapping

        except InvalidRequestError:
            # An SQL error will occur if the database is being spammed
            db_session.rollback()
            return f"Encountered an error please try again later."

        finally:
            db_session.close()

    def get_switch_by_id(self, id):
        try:
            db_session = models.Session()

            switch = db_session.query(models.Switch) \
                        .filter(models.Switch.id.like(f"{id}")) \
                        .all()

            if len(switch) == 1:
                return switch[0]

            return None

        except InvalidRequestError:
            # An SQL error will occur if the database is being spammed
            db_session.rollback()
            return f"Encountered an error please try again later."

        finally:
            db_session.close()