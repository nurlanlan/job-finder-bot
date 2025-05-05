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
            locale='az-AZ'
        )
        page = context.new_page()

        try:
            print("Loading job listings page...")
            page.goto(f"{BASE_URL}/vacancies", timeout=60000)
            time.sleep(3)  # Initial load

            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

            page.screenshot(path="debug_page.png")
            print("Saved screenshot to debug_page.png")

            job_elements = page.query_selector_all('''
                div.list_item,
                div.vacancy-item,
                div[class*="item"],
                div[class*="vacancy"],
                div[class*="job"]
            ''')

            print(f"Found {len(job_elements)} potential job elements")

            jobs = []
            seen_links = set()

            for element in job_elements:
                try:
                    link_element = element.query_selector('a[href*="/vacancies/"]')
                    if not link_element:
                        continue

                    link = link_element.get_attribute('href')
                    if not link or link in seen_links:
                        continue

                    seen_links.add(link)
                    full_link = f"{BASE_URL}{link}" if link.startswith('/') else link

                    title = element.query_selector('h3, h2, .title, [class*="title"]')
                    title_text = title.inner_text().strip() if title else "No Title"

                    date_element = element.query_selector('''
                        span.date, time, .post-date, 
                        [class*="date"], [class*="time"]
                    ''')
                    date_text = date_element.inner_text().strip().lower() if date_element else "unknown"

                    if 'bugün' in date_text or 'today' in date_text:
                        date_text = "today"
                    elif 'dünən' in date_text or 'yesterday' in date_text:
                        date_text = "yesterday"

                    jobs.append({
                        'title': title_text,
                        'link': full_link,
                        'date': date_text
                    })

                except Exception as e:
                    print(f"Error processing element: {str(e)}")
                    continue

            print(f"Extracted {len(jobs)} unique job listings")

            if not jobs:
                print("HTML content snippet:", page.content()[:2000])
                return

            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"jobsearch_results_{timestamp}.csv"

            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Job Title', 'Job Link', 'Posted Date'])

                for job in jobs:
                    writer.writerow([job['title'], job['link'], job['date']])

            print(f"Successfully saved to {csv_filename}")

        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            page.screenshot(path="error.png")
        finally:
            browser.close()


if __name__ == '__main__':
    scrape_jobsearch()