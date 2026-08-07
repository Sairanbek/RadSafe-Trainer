async def safe_answer(callback, *args, **kwargs):
    try:
        await callback.answer(*args, **kwargs)
    except Exception:
        pass