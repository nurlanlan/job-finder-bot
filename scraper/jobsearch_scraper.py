from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time

BASE_URL = 'https://www.jobsearch.az'


def scrape_jobsearch():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            java_script_enabled=True
        )
        page = context.new_page()

        try:
            print("Loading job listings page...")
            page.goto(f"{BASE_URL}/vacancies", timeout=60000, wait_until="networkidle")

            page.wait_for_selector('div.list_item, div.vacancy-item, [class*="item"]', timeout=15000)

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            job_cards = page.query_selector_all('div.list_item, div.vacancy-item, [class*="item"]')
            print(f"Found {len(job_cards)} job cards")

            if not job_cards:
                page.screenshot(path="debug_no_jobs.png")
                print("Saved screenshot to debug_no_jobs.png")
                print("HTML content:", page.content()[:1000])
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"jobsearch_results_{timestamp}.csv"

            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Job Title', 'Company', 'Location', 'Salary', 'Posted Date', 'Job Link'])

                for i, card in enumerate(job_cards, 1):
                    try:
                        title = card.query_selector('h3').inner_text().strip() if card.query_selector(
                            'h3') else "No Title"
                        link_element = card.query_selector('a[href*="/vacancies/"]')
                        link = link_element.get_attribute('href') if link_element else "No Link"
                        full_link = f"{BASE_URL}{link}" if link.startswith('/') else link

                        company = card.query_selector(
                            'div.company, span.company').inner_text().strip() if card.query_selector(
                            'div.company, span.company') else "N/A"
                        location = card.query_selector(
                            'span.location, div.location').inner_text().strip() if card.query_selector(
                            'span.location, div.location') else "N/A"
                        salary = card.query_selector(
                            'span.salary, div.salary').inner_text().strip() if card.query_selector(
                            'span.salary, div.salary') else "N/A"
                        date = card.query_selector('span.date, time').inner_text().strip() if card.query_selector(
                            'span.date, time') else "N/A"

                        writer.writerow([title, company, location, salary, date, full_link])
                        print(f"Processed job {i}: {title}")

                    except Exception as e:
                        print(f"Error processing job {i}: {str(e)}")
                        continue

            print(f"\nSuccessfully saved {len(job_cards)} jobs to {csv_filename}")

        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            page.screenshot(path="error_screenshot.png")
            print("Saved error screenshot to error_screenshot.png")
        finally:
            browser.close()


if __name__ == '__main__':
    scrape_jobsearch()