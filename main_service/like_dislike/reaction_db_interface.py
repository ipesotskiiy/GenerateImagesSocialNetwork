from sqlalchemy import select


class ReactionDBInterface:
    async def fetch_one(self, session, Model, reaction_data):
        reaction = await session.execute(
            select(Model).where(
                Model.user_id == reaction_data.user_id,
                Model.content_id == reaction_data.content_id,
                Model.content_type == reaction_data.content_type
            )
        )
        return reaction.scalars().first()

