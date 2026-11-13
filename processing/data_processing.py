"""Chuyển dữ liệu CSV gốc thành CSV đã xử lý."""
from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "dataset" / "data.csv"
OUTPUT_PATH = ROOT / "dataset" / "data_cleaned.csv"
TOPCV_INPUT_PATH = ROOT / "dataset" /  f"date={datetime.now().strftime('%Y-%m-%d')}" / "topcv_jobs.json"
TOPCV_OUTPUT_PATH = ROOT / "dataset" /  f"date={datetime.now().strftime('%Y-%m-%d')}" / "topcv_cleaned.csv"


def parse_salary_number(number_text, unit):
    if unit == "VND":
        number_text = number_text.replace(",", ".")
    elif unit == "USD":
        number_text = number_text.replace(",", "")

    return float(number_text)

def salary_to_numeric(salary):
    if pd.isna(salary):
        return np.nan, np.nan, np.nan

    value = str(salary).lower().strip()
    if "triệu" in value:
        unit = "VND"
    elif "usd" in value:
        unit = "USD"
    else:
        unit = np.nan

    if unit == "VND":
        pattern = r"\d+(?:[.,]\d+)?"
    elif unit == "USD":
        pattern = r"\d[\d,]*"
    else:
        pattern = r"\d+"

    if value in ('thỏa thuận', 'thoả thuận'):
        return np.nan, np.nan, np.nan

    elif value.startswith('trên') or value.startswith('từ'):
        number = re.search(pattern, value)
        if number:
            so = parse_salary_number(number.group(), unit)
            if "triệu" in value:
                so = so * 1000000
            return so, np.nan, unit
        
    elif value.startswith('tới'):
        number = re.search(pattern, value)
        if number:
            so = parse_salary_number(number.group(), unit)
            if "triệu" in value:
                so = so * 1000000
            return np.nan, so, unit
        
    else:
        numbers = re.findall(pattern, value)
        if len(numbers) == 2:
            so1 = parse_salary_number(numbers[0], unit)
            so2 = parse_salary_number(numbers[1], unit)
            if "triệu" in value:
                so1 = so1 * 1000000
                so2 = so2 * 1000000
            return so1, so2, unit
        elif len(numbers) == 1:
            so = parse_salary_number(numbers[0], unit)
            if "triệu" in value:
                so = so * 1000000
            return so, so, unit
    return np.nan, np.nan, unit

tinh_thanh = [
    "An Giang",
    "Bà Rịa - Vũng Tàu",
    "Bạc Liêu",
    "Bắc Giang",
    "Bắc Kạn",
    "Bắc Ninh",
    "Bến Tre",
    "Bình Dương",
    "Bình Định",
    "Bình Phước",
    "Bình Thuận",
    "Cà Mau",
    "Cao Bằng",
    "Cần Thơ",
    "Đà Nẵng",
    "Đắk Lắk",
    "Đắk Nông",
    "Điện Biên",
    "Đồng Nai",
    "Đồng Tháp",
    "Gia Lai",
    "Hà Giang",
    "Hà Nam",
    "Hà Nội",
    "Hà Tĩnh",
    "Hải Dương",
    "Hải Phòng",
    "Hậu Giang",
    "Hòa Bình",
    "Hồ Chí Minh",
    "Hưng Yên",
    "Huế",
    "Khánh Hòa",
    "Kiên Giang",
    "Kon Tum",
    "Lai Châu",
    "Lâm Đồng",
    "Lạng Sơn",
    "Lào Cai",
    "Long An",
    "Nam Định",
    "Nghệ An",
    "Ninh Bình",
    "Ninh Thuận",
    "Phú Thọ",
    "Phú Yên",
    "Quảng Bình",
    "Quảng Nam",
    "Quảng Ngãi",
    "Quảng Ninh",
    "Quảng Trị",
    "Sóc Trăng",
    "Sơn La",
    "Tây Ninh",
    "Thái Bình",
    "Thái Nguyên",
    "Thanh Hóa",
    "Tiền Giang",
    "Trà Vinh",
    "Tuyên Quang",
    "Vĩnh Long",
    "Vĩnh Phúc",
    "Yên Bái",
    "Toàn Quốc",
]

foreign_locations = [
    "Nhật Bản",
    "Hàn Quốc",
    "Trung Quốc",
    "Singapore",
    "Thái Lan",
    "Đài Loan",
    "Mỹ",
    "Hoa Kỳ",
    "Úc",
    "Canada",
    "Anh",
    "Đức",
    "Pháp",
    "Nước Ngoài",
]
def address_separate(location):
    if pd.isna(location):
        return {}
    location = re.sub(
        r"\s*\(mới\)",
        "",
        location,
        flags=re.IGNORECASE,
    )
    parts = [part.strip() for part in re.split(r"[:&]", location)]

    results = {}
    number_of_city = 0
    number_of_district = 0

    for part in parts:
        if part in tinh_thanh:
            number_of_city += 1
            number_of_district = 0
            results[f"city{number_of_city}"] = part
        elif number_of_city > 0:
            districts = part.split(",")

            for district in districts:
                district = district.strip()
                number_of_district += 1
                results[f"district{number_of_city}_{number_of_district}"] = district
        elif part in foreign_locations:
            number_of_city += 1
            number_of_district = 0
            results[f"city{number_of_city}"] = part
    return results

software_development = [
    "developer", "programmer", "software engineer",
    "software development", "lập trình", "phát triển phần mềm",
    "frontend", "front-end", "front end",
    "backend", "back-end", "back end",
    "fullstack", "full-stack", "full stack",
    "angularjs", "reactjs", "nodejs", "laravel",
    "javascript", "java", "python",
    "php", "c#", "c++", "golang",
]

testing = [
    "tester", "testing", "software test",
    "quality assurance", "quality control",
    "kiểm thử", "kiểm thử phần mềm",
]

business_develoment = [
    "business analyst", "business analysis",
    "phân tích nghiệp vụ", "business intelligence",
    "business development",  "kỹ sư cầu nối",
    "bridge engineer", "bridge software engineer", "brse engineer",
]

data_ai = [
    "data analyst", "data engineer", "data scientist",
    "data science", "data developer", "big data",
    "ai engineer", "machine learning",
    "phân tích dữ liệu", "quản trị cơ sở dữ liệu",
    "data admin",  "data governance",
]

security = [
    "security engineer", "security analyst",
    "application security", "pentester",
    "an toàn thông tin", "bảo mật",
]

it_support_infrastructure = [
    "it support", "it helpdesk", "help desk", "helpdesk",
    "system admin", "system engineer",
    "network engineer", "infra engineer", "it application support",
    "hỗ trợ kỹ thuật", "quản trị hệ thống", "quản trị mạng", "devops",
    "cloud engineer", "cloud architect", "cloud administrator", "triển khai phần mềm",
    "it infra","technical support","sre", "devsecops"
]

design = [
    "ui/ux", "ux/ui", "ui designer", "ux designer",
    "game designer", "game design", "2d artist", "3d artist",
    "web designer" , "graphic designer",
    "thiết kế đồ họa",
]

project_product_management = [
    "project manager", "project leader", "project coordinator",
    "product manager", "product owner", "scrum master",
    "quản lý dự án", "điều phối dự án", "comtor", "it communicator"
]

hardware = ["iot", "embedded", "nhúng", "cơ điện tử",
            "robotics", "robot", "cơ khí", "cơ khí chế tạo", "cơ khí động lực",
            "cơ khí ô tô", "cơ khí chính xác", "vi mạch",]

education = ["giáo viên", "giảng viên",]

it_support_infrastructure += [
    "kỹ sư hệ thống",
    "hệ thống mạng",
    "kỹ thuật mạng",
    "service desk",
    "linux engineer",
    "site reliability engineer",
    "server engineer",
    "triển khai hạ tầng",
    "vận hành cloud",
]

data_ai += [
    "database administrator",
    "database engineer",
    "computer vision",
    "ai intern",
    "thực tập sinh ai",
    "data manager",
]

testing += [
    "automation test",
    "test lead",
    "test leader",
    "test engineer",
]

software_development += [
    "mobile dev",
    "react native",
    "fresher android",
    "ruby on rails",
]

design += [
    "multimedia designer",
    "product designer",
    "thiết kế website",
]

marketing_content = [
    "marketing",
    "seo",
    "content writer",
    "content marketing",
    "video editor",
]

def classify_job_title(job_title):
    if pd.isna(job_title):
        return "Other"

    job_title_lower = job_title.lower()
    job_title_lower = job_title_lower.replace("_", " ")

    if re.search(r"\b(bi)\b", job_title_lower):
        return "Business Development/BI/BA"
    
    if re.search(r"\b(qa|qc|pqa)\b", job_title_lower):
        return "Testing"

    if re.search(r"\bbrse\b", job_title_lower):
        return "Business Development/BI/BA"

    
    for keyword in education:
        if keyword in job_title_lower:
            return "Education"
        
    for keyword in security:
        if keyword in job_title_lower:
            return "Security"

    for keyword in hardware:
        if keyword in job_title_lower:
            return "Hardware"
            
    for keyword in data_ai:
        if keyword in job_title_lower:
            return "Data & AI"

    for keyword in testing:
        if keyword in job_title_lower:
            return "Testing"

    for keyword in business_develoment:
        if keyword in job_title_lower:
            return "Business Development/BI/BA"

    for keyword in project_product_management:
        if keyword in job_title_lower:
            return "Project & Product Management"
            
    for keyword in design:
         if keyword in job_title_lower:
            return "Design"
         
    for keyword in marketing_content:
        if keyword in job_title_lower:
            return "Marketing & Content"
            
    for keyword in it_support_infrastructure:
        if keyword in job_title_lower:
            return "IT Support & Infrastructure"
                            
    for keyword in software_development:
        if keyword in job_title_lower:
            return "Software Development"
    
    return "Other"


def transform_data(df):
    df[["min_salary", "max_salary", "salary_unit"]] = (
        df["salary"].apply(salary_to_numeric).apply(pd.Series)
    )

    locations = df["address"].apply(address_separate).apply(pd.Series)
    df = pd.concat([df, locations], axis=1)

    df["job_title_category"] = df["job_title"].apply(classify_job_title)
    df["salary_avg"] = (df["min_salary"] + df["max_salary"]) / 2

    return df


def main():
    # Đọc CSV
    try:
        df_csv = pd.read_csv(INPUT_PATH)
    except FileNotFoundError as error:
        print(f"Không tìm thấy file CSV: {error}")
        raise
    except pd.errors.EmptyDataError:
        print(f"File CSV rỗng: {INPUT_PATH}")
        raise

    # Đọc JSON
    try:
        df_topcv = pd.read_json(TOPCV_INPUT_PATH)
    except FileNotFoundError as error:
        print(f"Không tìm thấy file JSON: {error}")
        raise
    except ValueError as error:
        print(f"Không đọc được JSON: {error}")
        raise
    if df_topcv.empty:
        print("JSON không có bản ghi nào.")
    df_csv = transform_data(df_csv)
    df_csv.to_csv(OUTPUT_PATH, index=False)

    df_topcv = transform_data(df_topcv)
    df_topcv.to_csv(TOPCV_OUTPUT_PATH, index=False)

    print(f"Đã lưu {len(df_csv)} dòng vào {OUTPUT_PATH}")
    print(f"Đã lưu {len(df_topcv)} dòng vào {TOPCV_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
