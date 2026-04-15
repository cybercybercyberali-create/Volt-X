import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_metals import omega_metals
from services.cards import gold_card
from config import GOLD_KARATS, METAL_NAMES, t

logger = logging.getLogger(__name__)
router = Router(name="gold")


@router.message(Command("gold"))
async def cmd_gold(message: Message, lang: str = "en") -> None:
    await message.answer(t("fetching", lang))
    try:
        data = await omega_metals.get_prices("XAU", "USD")
        if data.get("error"):
            await message.answer(t("error", lang))
            return

        # Enrich data with silver + platinum for the card
        try:
            ag = await omega_metals.get_prices("XAG", "USD")
            if not ag.get("error"):
                data["silver_per_ounce"] = ag.get("price_per_ounce", 0)
        except Exception:
            pass
        try:
            pt = await omega_metals.get_prices("XPT", "USD")
            if not pt.get("error"):
                data["platinum_per_ounce"] = pt.get("price_per_ounce", 0)
        except Exception:
            pass

        text = gold_card(data, lang)
        # Add karat detail if available
        if data.get("karats"):
            sep = "━━━━━━━━━━━━━━"
            karat_lines = [f"\n{sep}"]
            karat_label = "💛 أسعار الكيلو غرام" if lang == "ar" else "💛 Karat Prices (per gram)"
            karat_lines.append(karat_label)
            for k in ["24K", "22K", "21K", "18K", "14K", "9K"]:
                if k in data["karats"]:
                    karat_lines.append(f"  {k}: *${data['karats'][k]['per_gram']:,.2f}*")
            text += "\n".join(karat_lines)

        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_refresh", lang), callback_data="gold:refresh"),
             InlineKeyboardButton(text=t("btn_silver", lang), callback_data="metal:XAG"),
             InlineKeyboardButton(text=t("btn_platinum", lang), callback_data="metal:XPT")],
        ])
        await message.answer(text, parse_mode="Markdown", reply_markup=buttons)
    except Exception as exc:
        logger.error(f"Gold error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data.startswith("metal:"))
async def handle_metal(callback: CallbackQuery, lang: str = "en") -> None:
    metal = callback.data.split(":")[1]
    await callback.answer(t("fetching", lang))
    try:
        data = await omega_metals.get_prices(metal, "USD")
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return
        name = METAL_NAMES.get(metal, {}).get(lang, METAL_NAMES.get(metal, {}).get("en", metal))
        text = f"🪙 *{name}*\n\n💰 ${data['price_per_ounce']:,.2f}"
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Metal callback error: {exc}", exc_info=True)


@router.callback_query(lambda c: c.data == "gold:karats")
async def handle_gold_karats(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    try:
        data = await omega_metals.get_prices("XAU", "USD")
        if data.get("error") or not data.get("karats"):
            await callback.message.answer(t("error", lang))
            return
        text = t("gold_karats_title", lang) + "\n\n"
        for karat in ["24K", "22K", "21K", "18K", "14K", "10K", "9K"]:
            if karat in data["karats"]:
                text += f"  {karat}: ${data['karats'][karat]['per_gram']:,.2f}\n"
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Karats error: {exc}", exc_info=True)


@router.callback_query(lambda c: c.data == "gold:refresh")
async def handle_gold_refresh(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer(t("fetching", lang))
    from services.cache_service import cache
    await cache.delete("metals:XAU:USD")
    await cmd_gold(callback.message, lang=lang)


def register_gold_handlers(dp) -> None:
    dp.include_router(router)
