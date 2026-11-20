import json, logging, os
import anthropic

log = logging.getLogger(__name__)
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")
SYSTEM = "Bạn là trợ lý của câu lạc bộ sinh viên. Luôn trả lời bằng tiếng Việt, ngắn gọn, chính xác."


def ask_ai(prompt, fallback=""):
    """Trả về (text, ok)."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return fallback, False
    try:
        client = anthropic.Anthropic(api_key=key, timeout=25, max_retries=1)
        r = client.messages.create(
            model=MODEL, max_tokens=1200, system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.content[0].text, True
    except anthropic.APIError:
        log.exception("Gọi AI thất bại")
        return fallback, False


def suggest_tasks(minutes_text, members):
    """members: [{'id': 1, 'name': 'an', 'role': 'Ban điều hành'}, ...]"""
    prompt = (
        "Từ biên bản họp trong thẻ <minutes>, trích xuất các đầu việc và gán cho thành viên phù hợp "
        "theo vai trò. Chỉ dùng id trong danh sách. Trả về DUY NHẤT một mảng JSON, mỗi phần tử có: "
        '"title", "assignee_id", "due_date" (YYYY-MM-DD hoặc null), "reason".\n'
        f"<members>{json.dumps(members, ensure_ascii=False)}</members>\n"
        f"<minutes>{minutes_text}</minutes>"
    )
    text, ok = ask_ai(prompt)
    if not ok:
        return [], False
    try:
        text = text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(text), True
    except json.JSONDecodeError:
        return [], False

def _as_text(result):
    """ask_ai có thể trả về chuỗi hoặc tuple (text, ok); chuẩn hóa về chuỗi."""
    if isinstance(result, tuple):
        result = result[0]
    return result or ""


def draft_announcement(ev):
    title = getattr(ev, "title", "") or getattr(ev, "name", "") or "Sự kiện"
    description = getattr(ev, "description", "") or ""
    location = getattr(ev, "location", "") or ""
    start = getattr(ev, "start_time", None) or getattr(ev, "date", None) or ""

    prompt = (
        "Hãy viết một thông báo ngắn gọn, thân thiện bằng tiếng Việt cho sự kiện sau.\n"
        f"Tên sự kiện: {title}\n"
        f"Thời gian: {start}\n"
        f"Địa điểm: {location}\n"
        f"Mô tả: {description}\n"
        "Chỉ trả về nội dung thông báo."
    )
    fallback = f"Thông báo: {title}\nThời gian: {start}\nĐịa điểm: {location}".strip()
    return _as_text(ask_ai(prompt, fallback=fallback))


def summarize_minutes(text, roles=None):
    prompt = (
        "Hãy tóm tắt biên bản họp sau thành các ý chính "
        "(quyết định, việc cần làm, người phụ trách) bằng tiếng Việt.\n"
        f"Các vai trò trong CLB: {roles or ''}\n\n"
        f"{text}"
    )
    fallback = (text or "")[:300]
    return _as_text(ask_ai(prompt, fallback=fallback))