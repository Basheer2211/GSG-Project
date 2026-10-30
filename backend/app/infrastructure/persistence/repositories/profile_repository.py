
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.domain.entities.profile import Profile
from app.domain.interfaces.profile_repository import IProfileRepository
from app.infrastructure.persistence.models.profile_model import ProfileModel


class ProfileRepository(IProfileRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
        self,
        user_id: int
    ) -> Profile | None:

        stmt = select(ProfileModel).where(
            ProfileModel.user_id == user_id
        )

        model = self.db.scalar(stmt)

        if model is None:
            return None

        return self._to_entity(model)

    def get_or_create_by_user_id(
        self,
        user_id: int
    ) -> Profile:

        stmt = (
            insert(ProfileModel)
            .values(user_id=user_id)
            .on_conflict_do_nothing(
                index_elements=[ProfileModel.user_id]
            )
        )

        self.db.execute(stmt)
        self.db.flush()

        profile = self.get_by_user_id(user_id)

        if profile is None:
            raise RuntimeError(
                "Failed to get or create profile"
            )

        return profile

    @staticmethod
    def _to_entity(
        model: ProfileModel
    ) -> Profile:

        return Profile(
            profile_id=model.profile_id,
            user_id=model.user_id,
            full_name=model.full_name,
            email=model.email,
            phone=model.phone,
            city=model.city,
            title=model.title,
            country_id=model.country_id
        )
