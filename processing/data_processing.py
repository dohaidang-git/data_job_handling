"""Chuyển dữ liệu CSV gốc thành CSV đã xử lý."""
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "dataset" / "data.csv"
OUTPUT_PATH = ROOT / "dataset" / "data_cleaned.csv"

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

    if value in ('thỏa thuận', 'thoả thuận'):
        return np.nan, np.nan, np.nan
    
    elif value.startswith('trên'):
        number = re.search(r"\d[\d,]*", value)
        if number:
            so = float(number.group().replace(',', ''))
            if "triệu" in value:
                so = so * 1000000
            return so, np.nan, unit
        
    elif value.startswith('tới'):
        number = re.search(r"\d[\d,]*", value)
        if number:
            so = float(number.group().replace(',', ''))
            if "triệu" in value:
                so = so * 1000000
            return np.nan, so, unit
        
    else:
        numbers = re.findall(r"\d[\d,]*", value)
        if len(numbers) == 2:
            so1 = float(numbers[0].replace(',', ''))
            so2 = float(numbers[1].replace(',', ''))
            if "triệu" in value:
                so1 = so1 * 1000000
                so2 = so2 * 1000000
            return so1, so2, unit
        elif len(numbers) == 1:
            so = float(numbers[0].replace(',', ''))
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

def address_separate(location):
    if pd.isna(location):
        return {}

    parts = [part.strip() for part in location.split(":")]

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

    return results

software_development = [
    "developer", "programmer", "software engineer",
    "software development", "lập trình", "phát triển phần mềm",
    "frontend", "front-end", "front end",
    "backend", "back-end", "back end",
    "fullstack", "full-stack", "full stack",
    "angularjs", "reactjs", "nodejs", "laravel"
]

software_testing = [
    "tester", "testing", "software test",
    "quality assurance", "quality control",
    "kiểm thử", "kiểm thử phần mềm",
]

business_analysis = [
    "business analyst", "business analysis",
    "phân tích nghiệp vụ", "business intelligence", "bi"
]

data_ai = [
    "data analyst", "data engineer", "data scientist",
    "data science", "data developer", "big data",
    "ai engineer", "machine learning",
    "phân tích dữ liệu", "quản trị cơ sở dữ liệu",
    "data admin",
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
    "quản lý dự án", "điều phối dự án",
]

hardware = ["iot", "embedded", "nhúng", "cơ điện tử",
            "robotics", "robot", "cơ khí", "cơ khí chế tạo", "cơ khí động lực",
            "cơ khí ô tô", "cơ khí chính xác", "vi mạch",]

def classify_job_title(job_title):
    if pd.isna(job_title):
        return "Other"

    job_title_lower = job_title.lower()

    for keyword in security:
            if keyword in job_title_lower:
                return "Security"

    for keyword in data_ai:
            if keyword in job_title_lower:
                return "Data & AI"

    for keyword in software_testing:
            if keyword in job_title_lower:
                return "Software Testing"

    for keyword in business_analysis:
            if keyword in job_title_lower:
                return "Business Analysis"

    for keyword in project_product_management:
            if keyword in job_title_lower:
                return "Project & Product Management"
            
    for keyword in design:
            if keyword in job_title_lower:
                return "Design"
            
    for keyword in it_support_infrastructure:
            if keyword in job_title_lower:
                return "IT Support & Infrastructure"
            
    for keyword in software_development:
        if keyword in job_title_lower:
            return "Software Development"
    for keyword in hardware:
        if keyword in job_title_lower:
            return "Hardware"
    return "Other"

def main():
    df = pd.read_csv(INPUT_PATH)
    df[["min_salary", "max_salary", "salary_unit"]] = (
        df["salary"].apply(salary_to_numeric).apply(pd.Series)
    )
    locations = df["address"].apply(address_separate).apply(pd.Series)
    df = pd.concat([df, locations], axis=1)
    df["job_title_category"] = df["job_title"].apply(classify_job_title)
    df["salary_avg"] = (df["min_salary"] + df["max_salary"]) / 2
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Đã lưu {len(df)} dòng vào {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
