async def create_user(telegram_id, username, name):

    user = User(
        telegram_id=telegram_id,
        username=username,
        name=name
    )

    async with async_session() as session:
        session.add(user)
        await session.commit()


async def get_user(telegram_id):

    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()


async def get_user_progress(telegram_id):

    return {
        "tests": 0,
        "average": 0
    }