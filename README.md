# ClubHub - Quản lý CLB sinh viên (Django)

## Chạy local (PowerShell)
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
Đặt `ANTHROPIC_API_KEY` để bật AI (không có key vẫn chạy, dùng mẫu thông báo).

## Deploy Render
1. Push code lên GitHub.
2. Render > New > Blueprint > chọn repo (đọc `render.yaml`).
3. Đặt `DJANGO_SUPERUSER_PASSWORD` và `ANTHROPIC_API_KEY` trong Environment.
4. Sau khi deploy xong dùng URL `https://<tên>.onrender.com`. Đăng nhập admin, vào "Thành viên" để phân quyền.
