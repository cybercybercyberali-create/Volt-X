import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)
router = Router(name="cv")


class CVStates(StatesGroup):
    full_name = State()
    email = State()
    phone = State()
    summary = State()
    experience = State()
    education = State()
    skills = State()
    languages = State()
    template = State()


@router.message(Command("cv"))
async def cmd_cv(message: Message, state: FSMContext, lang: str = "en") -> None:
    await state.update_data(lang=lang)
    await state.set_state(CVStates.full_name)
    await message.answer(
        t("cv_intro", lang) + "\n\n" + t("cv_step", lang, n="1", q=t("cv_q_name", lang)),
        parse_mode="Markdown"
    )


@router.message(CVStates.full_name)
async def process_name(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(full_name=message.text)
    await state.set_state(CVStates.email)
    await message.answer(t("cv_step", lang, n="2", q=t("cv_q_email", lang)), parse_mode="Markdown")


@router.message(CVStates.email)
async def process_email(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(email=message.text)
    await state.set_state(CVStates.phone)
    await message.answer(t("cv_step", lang, n="3", q=t("cv_q_phone", lang)), parse_mode="Markdown")


@router.message(CVStates.phone)
async def process_phone(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(phone=message.text)
    await state.set_state(CVStates.summary)
    await message.answer(t("cv_step", lang, n="4", q=t("cv_q_summary", lang)), parse_mode="Markdown")


@router.message(CVStates.summary)
async def process_summary(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(summary=message.text)
    await state.set_state(CVStates.experience)
    await message.answer(t("cv_step", lang, n="5", q=t("cv_q_experience", lang)), parse_mode="Markdown")


@router.message(CVStates.experience)
async def process_experience(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(experience=message.text)
    await state.set_state(CVStates.education)
    await message.answer(t("cv_step", lang, n="6", q=t("cv_q_education", lang)), parse_mode="Markdown")


@router.message(CVStates.education)
async def process_education(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(education=message.text)
    await state.set_state(CVStates.skills)
    await message.answer(t("cv_step", lang, n="7", q=t("cv_q_skills", lang)), parse_mode="Markdown")


@router.message(CVStates.skills)
async def process_skills(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(skills=message.text)
    await state.set_state(CVStates.languages)
    await message.answer(t("cv_step", lang, n="8", q=t("cv_q_languages", lang)), parse_mode="Markdown")


@router.message(CVStates.languages)
async def process_languages(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(languages=message.text)
    await state.set_state(CVStates.template)
    await message.answer(
        t("cv_step", lang, n="9", q=t("cv_q_template", lang)) + "\n1. Modern\n2. Classic\n3. Creative\n4. Minimal\n5. Professional",
        parse_mode="Markdown"
    )


@router.message(CVStates.template)
async def process_template(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    templates = {"1": "modern", "2": "classic", "3": "creative", "4": "minimal", "5": "professional"}
    template = templates.get(message.text.strip(), "modern")
    state_data["template"] = template
    data = state_data
    await state.clear()

    await message.answer(t("cv_generating", lang))

    try:
        from services.omega_query_engine import query_engine

        prompt = f"""Improve this CV professionally:
Name: {data.get('full_name', '')}
Summary: {data.get('summary', '')}
Experience: {data.get('experience', '')}
Education: {data.get('education', '')}
Skills: {data.get('skills', '')}
Languages: {data.get('languages', '')}

Return improved bullet points for each section. Be concise and professional."""

        lang_instruction = f"Respond in the same language as the CV data." 
        responses = await query_engine.query_all(prompt, system_prompt=f"You are a professional CV writer. {lang_instruction}")
        improved_text = responses[0]["text"] if responses else data.get("summary", "")

        await message.answer(
            t("cv_done", lang) + f"\n\n"
            f"📄 {template}\n"
            f"👤 {data.get('full_name', '')}\n\n"
            f"{improved_text[:500]}",
            parse_mode="Markdown"
        )

    except Exception as exc:
        logger.error(f"CV generation error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_cv_handlers(dp) -> None:
    dp.include_router(router)
