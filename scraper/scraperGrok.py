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
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()

        try:
            print("Loading job listings page...")
            page.goto(f"{BASE_URL}/vacancies", timeout=60000)
            time.sleep(3)  # Initial load

            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)

            jobs = page.evaluate('''() => {
                const items = [];
                document.querySelectorAll('a[href*="/vacancies/"]').forEach(a => {
                    const title = a.querySelector('h3')?.innerText.trim() || 'No Title';
                    items.push({
                        title: title,
                        link: a.href,
                        date: new Date().toISOString()  // Current time as fallback
                    });
                });
                return items;
            }''')

            print(f"Found {len(jobs)} jobs")

            if not jobs:
                page.screenshot(path="debug_no_jobs.png")
                print("No jobs found - saved screenshot to debug_no_jobs.png")
                return

            # Prepare CSV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"jobsearch_titles_links_{timestamp}.csv"

            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Job Title', 'Job Link', 'Scraped Date'])

                for job in jobs:
                    writer.writerow([job['title'], job['link'], job['date']])

            print(f"Successfully saved {len(jobs)} jobs to {csv_filename}")

        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            page.screenshot(path="error_screenshot.png")
        finally:
            browser.close()


if __name__ == '__main__':
    scrape_jobsearch()