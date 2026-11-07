import os


def ask_ai(prompt, fallback):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return fallback
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        r = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=900,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.content[0].text
    except Exception as e:
        return f"{fallback}\n\n(Không gọi được AI: {e})"


def draft_announcement(event):
    when = event.start_time.strftime("%H:%M %d/%m/%Y")
    fallback = (f"📢 THÔNG BÁO SỰ KIỆN\n{event.title}\n🕒 {when}\n📍 {event.location}\n"
                f"{event.description}\nMong các bạn tham gia đầy đủ!")
    prompt = ("Viết thông báo sự kiện ngắn gọn, thân thiện, tiếng Việt cho câu lạc bộ sinh viên.\n"
              f"Tên: {event.title}\nThời gian: {when}\nĐịa điểm: {event.location}\nMô tả: {event.description}")
    return ask_ai(prompt, fallback)


def summarize_minutes(text, member_roles):
    fallback = "Tóm tắt (chưa cấu hình AI):\n" + text[:500]
    prompt = ("Tóm tắt biên bản họp sau bằng tiếng Việt thành các gạch đầu dòng, sau đó đề xuất "
              "danh sách task (ai làm gì, hạn) dựa trên vai trò thành viên.\n"
              f"Thành viên: {member_roles}\n\nBiên bản:\n{text}")
    return ask_ai(prompt, fallback)
