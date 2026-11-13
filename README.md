# Pipeline dữ liệu tuyển dụng

Pipeline thu thập tin TopCV, xử lý dữ liệu từ TopCV và CSV có sẵn, rồi import vào PostgreSQL. Chạy các lệnh bên dưới từ thư mục gốc dự án.

## 1. Chuẩn bị môi trường

Cần Python, PostgreSQL qua Docker Compose và trình duyệt Chromium của Playwright.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pandas numpy playwright python-dotenv sqlalchemy psycopg2-binary matplotlib seaborn
python -m playwright install chromium
```

Tạo file `.env` tại thư mục gốc với thông tin kết nối riêng của bạn:

```dotenv
DB_USER=jobs_user
DB_PASSWORD=mat_khau_cua_ban
DB_HOST=localhost
DB_PORT=5433
DB_NAME=jobs_db
```

Không đưa `.env` lên Git. Với Compose hiện tại, PostgreSQL lắng nghe tại `localhost:5433`. Các biến khởi tạo PostgreSQL chỉ có hiệu lực khi volume dữ liệu được tạo lần đầu; đổi `.env` sau đó không tự đổi tài khoản hoặc mật khẩu đã lưu.

Khởi động và kiểm tra database:

```bash
docker compose up -d
docker compose ps
```

## 2. Thu thập TopCV

```bash
python -m crawler.topcv_crawler
```

Crawler chạy trình duyệt và lưu tin vào `dataset/date=YYYY-MM-DD/topcv_jobs.json`; checkpoint nằm cùng thư mục. Nếu bị gián đoạn, lần chạy sau trong cùng ngày sẽ đọc checkpoint và JSON hiện có. Việc phân trang có thể thay đổi trong lúc cào; checkpoint và lọc trùng không bảo đảm không bỏ sót tin. Cần kiểm tra quy định truy cập của nguồn trước khi thu thập.

## 3. Xử lý hai nguồn

Đảm bảo các file sau tồn tại:

- `dataset/data.csv`: dữ liệu CSV ban đầu.
- `dataset/date=YYYY-MM-DD/topcv_jobs.json`: dữ liệu TopCV của ngày chạy.

```bash
python -m processing.data_processing
```

Kết quả là `dataset/data_cleaned.csv` và `dataset/date=YYYY-MM-DD/topcv_cleaned.csv`. Script hiện chọn thư mục TopCV theo ngày hệ thống; muốn xử lý ngày khác cần điều chỉnh đường dẫn trong code. Chạy lại sẽ ghi đè CSV đầu ra.

## 4. Chuẩn bị bảng PostgreSQL

Trước khi import, bảng `public.jobs` phải có **tất cả cột** trong hai CSV đã xử lý, thêm cột `job_key` và ràng buộc `UNIQUE` trên cột này. Các cột địa điểm có thể khác nhau giữa hai nguồn; kiểm tra hợp các cột trước khi tạo hoặc điều chỉnh bảng. `to_sql` có thể tự tạo bảng nếu chưa tồn tại nhưng không tự tạo ràng buộc cần cho `ON CONFLICT`.

Nếu bảng đã có cấu trúc phù hợp nhưng chưa có `job_key`, chạy trong DBeaver:

```sql
ALTER TABLE public.jobs ADD COLUMN job_key TEXT;
ALTER TABLE public.jobs
    ADD CONSTRAINT jobs_job_key_unique UNIQUE (job_key);
```

Chỉ chạy các lệnh tương ứng nếu cột hoặc ràng buộc chưa tồn tại. Dữ liệu cũ sẽ có `job_key` là `NULL`; cần xử lý các dòng đó trước nếu muốn chống trùng với lần import mới. Kiểm tra schema và dữ liệu trước khi thay đổi bảng.

## 5. Import vào PostgreSQL

```bash
python -m processing.import_to_sql
```

Script đọc hai CSV đã xử lý, tạo khóa `csv_<hash>` từ link nguồn cũ và `topcv_<id>` từ ID TopCV. Các dòng không tạo được khóa được báo số lượng rồi bỏ qua. Lệnh import dùng `ON CONFLICT DO NOTHING` với `job_key`; bản ghi đã có sẽ không được cập nhật. Việc bỏ query khỏi link CSV giả định query không phân biệt tin tuyển dụng.

Kiểm tra trong DBeaver:

```sql
SELECT COUNT(*) FROM public.jobs;
SELECT * FROM public.jobs LIMIT 10;
```

Thông báo số dòng được xử lý trong script là số dòng hợp lệ trước khi ghi, không nhất thiết là số dòng mới được thêm.

## 6. Vẽ biểu đồ

```bash
python -m processing.visualization
```

Script hiện đọc `dataset/data_cleaned.csv` và hiển thị các biểu đồ; kiểm tra file nguồn của script nếu muốn vẽ dữ liệu TopCV hoặc dữ liệu gộp.

## 7. Chạy test

```bash
python -m unittest discover -s test -v
```

Integration test PostgreSQL là tùy chọn, dùng kết nối trong `.env` và tạo bảng tạm tự xóa:

```bash
RUN_POSTGRES_TESTS=1 python -m unittest discover -s test -p 'test_import_to_sql.py' -v
```

## 8. Lịch chạy hằng tuần

Crontab của người dùng hiện được cấu hình chạy lúc **07:00 thứ Hai hằng tuần**, theo múi giờ Việt Nam:

```cron
CRON_TZ=Asia/Ho_Chi_Minh
0 7 * * 1 cd /home/dohaidang/DEC-K29-DHD/Project/mini_project_action && /usr/bin/python -m crawler.topcv_crawler && /đường/dẫn/python -m processing.data_processing && /đường/dẫn/python -m processing.import_to_sql >> /home/dohaidang/DEC-K29-DHD/Project/mini_project_action/pipeline.log 2>&1
```

**Lịch này chưa sẵn sàng chạy đầy đủ:** hai đường dẫn `/đường/dẫn/python` vẫn là giá trị mẫu và cần thay bằng đường dẫn Python thực tế. Lệnh chuyển hướng log hiện chỉ áp dụng cho bước import cuối cùng. Crawler cũng đang chạy `headless=False`; cron có thể không có giao diện đồ họa. Nếu crawler dừng do timeout nhưng thoát thành công, hai bước sau vẫn có thể chạy với dữ liệu chưa đầy đủ.

Xem hoặc chỉnh sửa lịch bằng:

```bash
crontab -l
crontab -e
```

Máy cần hoạt động vào thời điểm chạy và PostgreSQL cần sẵn sàng nhận kết nối.
