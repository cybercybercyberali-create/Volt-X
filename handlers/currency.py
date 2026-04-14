import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_currency import omega_currency
from config import t

logger = logging.getLogger(__name__)
router = Router(name="currency")


def _stale_note(lang: str) -> str:
    return "\n\n⚠️ _البيانات الحية غير متاحة — يُعرض آخر سعر معروف_" if lang == "ar" \
        else "\n\n⚠️ _Live data unavailable — showing last known rate_"


@router.message(Command("currency"))
async def cmd_currency(message: Message, lang: str = "en") -> None:
    # Parse args: /currency USD EUR  OR called from NL routing (message.text is full sentence)
    raw = message.text or ""
    # Only trust args if the message starts with /currency
    if raw.strip().startswith("/currency"):
        parts = raw.split()[1:]
        base = parts[0].upper() if len(parts) >= 1 else "USD"
        target = parts[1].upper() if len(parts) >= 2 else None
    else:
        # Natural language: default to USD multi-rate view
        base = "USD"
        target = None

    await message.answer(t("fetching", lang))
    try:
        if target:
            data = await omega_currency.get_rate(base, target)
            if data.get("error"):
                await message.answer(t("error", lang))
                return
            rate_fmt = f"{data['rate']:,.2f}" if data['rate'] > 100 else f"{data['rate']:,.4f}"
            text = f"💱 *{base} → {target}*\n\n"
            text += f"  1 {base} = `{rate_fmt}` {target}\n"
            if data.get("has_parallel") and data.get("parallel_rate"):
                text += f"  📊 السوق الموازي: `{data['parallel_rate']:,.0f}`\n"
            if data.get("stale"):
                text += _stale_note(lang)

        else:
            data = await omega_currency.get_multiple_rates(base)
            lines = []
            any_stale = False
            for cur, info in data.items():
                if info.get("error"):
                    continue
                rate = info["rate"]
                rate_fmt = f"{rate:,.0f}" if rate > 1000 else (f"{rate:,.2f}" if rate > 10 else f"{rate:,.4f}")
                stale_mark = " ⚠️" if info.get("stale") else ""
                parallel = ""
                if info.get("has_parallel") and info.get("parallel_rate"):
                    parallel = f" _(موازي: {info['parallel_rate']:,.0f})_"
                lines.append(f"  `{cur}` {rate_fmt}{stale_mark}{parallel}")
                if info.get("stale"):
                    any_stale = True

            if not lines:
                await message.answer(t("error", lang))
                return

            text = f"💱 *أسعار الصرف — أساس: {base}*\n\n" if lang == "ar" \
                else f"💱 *Exchange Rates — Base: {base}*\n\n"
            text += "\n".join(lines)
            if any_stale:
                text += _stale_note(lang)

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Currency error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_currency_handlers(dp) -> None:
    dp.include_router(router)
