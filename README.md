# ClubHub - Quản lý Câu lạc bộ Sinh viên (Django)

Hệ thống web hỗ trợ quản lý toàn diện câu lạc bộ sinh viên: tổ chức sự kiện, điểm danh bằng QR code, phân công công việc, quản lý thu chi quỹ, báo cáo hoạt động và tích hợp AI hỗ trợ soạn thông báo / bóc tách việc từ biên bản họp.

---

## 🌟 Chức năng chính & Luồng hoạt động

```
[Ban điều hành] ─── Tạo sự kiện ───> [Hệ thống sinh QR Code] ───> [Thành viên quét QR để Điểm danh]
        │
        ├─── Nhập biên bản họp ───> [Claude AI Tóm tắt & Trích xuất Task] ───> [Tạo Task phân công]
        │
        ├─── Ghi nhận Thu / Chi ───> [Kiểm soát Số dư Quỹ (Chặn bội chi)]
        │
        └─── Báo cáo & Thống kê ───> [Đánh giá mức độ tương tác & Cảnh báo thành viên vắng nhiều]
```

### 1. Quản lý sự kiện & Điểm danh QR Code
- **Tạo sự kiện**: Ban điều hành tạo sự kiện với thời gian, địa điểm, mô tả.
- **Mã QR Check-in**: Mỗi sự kiện tự động sinh một mã QR chứa token bảo mật duy nhất (`uuid4`).
- **Điểm danh tức thì**: Thành viên quét QR hoặc truy cập link điểm danh; hệ thống ghi nhận thời gian tham gia và ngăn chặn điểm danh trùng lặp.

### 2. Quản lý công việc (Task)
- Phân công nhiệm vụ theo sự kiện hoặc công việc thường nhật.
- 3 trạng thái công việc: `Cần làm` (todo) ➔ `Đang làm` (doing) ➔ `Hoàn thành` (done).
- Thành viên chỉ thấy công việc của mình; Ban điều hành theo dõi toàn bộ tiến độ và cảnh báo việc quá hạn.

### 3. Trợ lý AI (Anthropic Claude)
- **Soạn thông báo sự kiện tự động**: Tạo nội dung truyền thông ngắn gọn, hấp dẫn dựa trên thông tin sự kiện. Hỗ trợ tính năng Xem trước, Áp dụng vào nội dung chính hoặc Hoàn tác (Undo).
- **Trích xuất task từ biên bản họp**: AI đọc biên bản họp, tóm tắt quyết định quan trọng và tự động gán đầu việc cho thành viên phù hợp theo vai trò. BĐH có thể chọn lọc và tạo task hàng loạt với 1 click.
*(Nếu không có API Key, hệ thống tự động fallback về mẫu thông báo mặc định mà không gây gián đoạn ứng dụng).*

### 4. Quản lý Quỹ & Tài chính
- Ghi nhận chi tiết các khoản Thu / Chi gắn liền với sự kiện hoặc hoạt động CLB.
- Tự động tính toán số dư quỹ theo thời gian thực; kiểm tra và chặn giao dịch chi nếu vượt quá số dư hiện có.
- Chỉ Admin có quyền xóa giao dịch để đảm bảo minh bạch.

### 5. Báo cáo & Đánh giá tương tác
- **Báo cáo tương tác (Engagement)**: Theo dõi tần suất tham gia sự kiện, số task quá hạn; tự động gắn cờ thành viên ít tương tác (tỉ lệ tham gia < 30% hoặc nợ >= 2 task).
- **Báo cáo hoạt động (Activity)**: Báo cáo tổng thể theo chu kỳ (30, 90, 180, 365 ngày) về tỷ lệ điểm danh, tiến độ công việc và dòng tiền thu/chi.

### 6. Phân quyền người dùng (RBAC)
- **Admin**: Toàn quyền hệ thống, thay đổi vai trò người dùng, xóa giao dịch tài chính.
- **Ban điều hành (Officer)**: Tạo sự kiện, tạo QR, giao task, dùng AI, quản lý thu chi, xem báo cáo.
- **Thành viên (Member)**: Xem sự kiện, quét QR điểm danh, cập nhật trạng thái các task được giao.

---

## 📁 Cấu trúc thư mục

```text
qlclub_py/
├── clubs/                  # Ứng dụng chính quản lý CLB
│   ├── ai.py               # Tích hợp Anthropic Claude (soạn thông báo, phân tích biên bản)
│   ├── forms.py            # Form đăng ký, sự kiện, task, thu chi, biên bản
│   ├── models.py           # Models: Profile, Event, Attendance, Task, Transaction
│   ├── services.py         # Nghiệp vụ thống kê & xuất báo cáo (engagement, activity)
│   ├── templates/clubs/    # Giao diện HTML (Tailwind CSS phong cách hiện đại)
│   ├── urls.py             # Định tuyến URL của ứng dụng
│   └── views.py            # Xử lý logic và phân quyền (role_required)
├── config/                 # Cấu hình dự án Django (settings, wsgi, urls)
├── build.sh                # Script build và migrate cho deploy production
├── render.yaml             # Blueprint cấu hình hạ tầng Render (Web + PostgreSQL)
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── manage.py
└── README.md
```

---

## 🚀 Hướng dẫn chạy cục bộ (Local Development)

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên (khuyên dùng Python 3.12).
- Git.

### 2. Cài đặt môi trường

**Trên Linux / macOS:**
```bash
git clone <repo-url>
cd qlclub_py

# Khởi tạo và kích hoạt virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

**Trên Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường (Tùy chọn)
Tạo file `.env` hoặc export biến môi trường:
```bash
export SECRET_KEY="your-secret-key"
export DEBUG="1"
export ANTHROPIC_API_KEY="sk-ant-..."   # Tùy chọn: để kích hoạt tính năng AI
```
*(Nếu không đặt `ANTHROPIC_API_KEY`, ứng dụng vẫn hoạt động bình thường với cơ chế fallback nội bộ).*

### 4. Khởi tạo Database & Tài khoản quản trị
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Chạy ứng dụng
```bash
python manage.py runserver
```
Truy cập trình duyệt tại: `http://127.0.0.1:8000/`. Đăng nhập bằng tài khoản superuser vừa tạo. Vào mục **Thành viên** để phân quyền Ban điều hành / Thành viên.

---

## 🌐 Hướng dẫn Triển khai (Deploy Render)

Dự án đã tích hợp sẵn tệp cấu hình `render.yaml` (Render Blueprint):

1. Đẩy mã nguồn lên repository GitHub / GitLab cá nhân.
2. Đăng nhập vào [Render.com](https://render.com) > Chọn **New** > **Blueprint**.
3. Kết nối với repo chứa mã nguồn. Render sẽ tự động nhận diện cấu hình:
   - **Web Service**: Chạy Gunicorn với lệnh build từ `build.sh`.
   - **Database**: PostgreSQL (Free plan).
4. Thiết lập các biến môi trường bắt buộc trong trang cấu hình Render:
   - `DJANGO_SUPERUSER_PASSWORD`: Mật khẩu cho tài khoản `admin`.
   - `ANTHROPIC_API_KEY`: API Key Anthropic để dùng tính năng AI (tùy chọn).
5. Nhấn **Apply**. Sau khi deploy xong, truy cập link `https://<ten-ung-dung>.onrender.com` để sử dụng.
