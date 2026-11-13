import json
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

URL = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "dataset" / f"date={datetime.now().strftime('%Y-%m-%d')}" / "topcv_jobs.json"
CHECKPOINT_PATH = OUTPUT_PATH.parent / "checkpoint.json"

def text_crawling(card, selector):
    element = card.locator(selector).first
    if element.count() == 0:
        return None
    
    return element.inner_text().strip()


def get_job_id(link):
    if not link:
        return None

    match = re.search(r"(?:/|-j)(\d+)\.html", link)
    return match.group(1) if match else None

def main():
    created_date = datetime.now().strftime("%Y-%m-%d")
    jobs = []
    next_page = 1

    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, "r", encoding="utf-8") as file:
            jobs = json.load(file)

    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as file:
            checkpoint = json.load(file)
            next_page = checkpoint["next_page"]

    print(f"Tiếp tục từ trang {next_page}, đã có {len(jobs)} tin.")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

        try:
            page = browser.new_page()
            start_url = f"{URL}?page={next_page}"

            page.goto(start_url, wait_until="domcontentloaded", timeout=30000)
            page.locator(".job-item-search-result").first.wait_for(
                state="attached",
                timeout=30000,
            )
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            seen_ids = {
                job_id
                for job in jobs
                if (job_id := get_job_id(job.get("link_description")))
            }
            while True:
                job_cards = page.locator(".job-item-search-result")
                print(f"Tìm thấy {job_cards.count()} tin")

                for i in range(job_cards.count()):
                    card = job_cards.nth(i)
                    job_id = card.get_attribute("data-job-id")

                    if job_id and job_id in seen_ids:
                        continue
                    title_link = card.locator("h3.title a").first

                    job = {
                        "created_date": created_date,
                        "job_title": text_crawling(card, "h3.title a"),
                        "company": text_crawling(card, ".company-name"),
                        "salary": text_crawling(card, ".title-salary"),
                        "address": text_crawling(card, ".city-text"),
                        "time": text_crawling(card, ".label-update"),
                        "link_description": (
                            title_link.get_attribute("href")
                            if title_link.count() > 0
                            else None
                        ),
                    }

                    jobs.append(job)
                    if job_id:
                        seen_ids.add(job_id)
                
                with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
                    json.dump(jobs, file, ensure_ascii=False, indent=2)
                next_page += 1

                with open(CHECKPOINT_PATH, "w", encoding="utf-8") as file:
                    json.dump({"next_page": next_page}, file)

                print(f"Đã lưu checkpoint: trang tiếp theo là {next_page}")       
                print(f"Đã lưu {len(jobs)} tin.")

                job_cards = page.locator(".job-item-search-result")
                                
                page_label = page.locator("#job-listing-paginate-text")
                previous_page = page_label.inner_text().strip()
                next_button = page.locator('nav.box-pagination a[rel="next"]')

                if next_button.count() == 0:
                    print("Không còn trang tiếp theo.")
                    break

                next_button.click()

                try:                
                    page.wait_for_function(
                        """previousPage => {
                            const label = document.querySelector("#job-listing-paginate-text");
                            return label && label.innerText.trim() !== previousPage;
                        }""",
                        arg=previous_page,
                        timeout=30000,
                    )
                except PlaywrightTimeoutError:
                    print(f"Không thấy trang thay đổi sau: {previous_page}")
                    print(f"URL hiện tại: {page.url}")
                    print(f"Tiêu đề trang: {page.title()}")
                    break
        finally:
            browser.close()

    print(f"Đã lưu {len(jobs)} tin vào {OUTPUT_PATH}")


if __name__ == "__main__":
    main()