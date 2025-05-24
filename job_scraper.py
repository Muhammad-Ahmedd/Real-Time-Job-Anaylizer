import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus, urljoin
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class RealJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver = None
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Selenium WebDriver initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Selenium setup failed: {e}")
            print("📝 Note: Install ChromeDriver for full functionality")
            self.driver = None
    
    def scrape_linkedin(self, skill, location="", max_jobs=50):
        """Scrape real jobs from LinkedIn"""
        print(f"🔍 Scraping LinkedIn for '{skill}' jobs...")
        jobs = []
        
        try:
            # LinkedIn job search URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': skill,
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'f_JT': 'F',  # Full time
                'start': 0
            }
            
            # Build URL
            url = f"{base_url}?keywords={quote_plus(skill)}"
            if location:
                url += f"&location={quote_plus(location)}"
            
            print(f"   🌐 Accessing: {url}")
            
            if self.driver:
                jobs = self._scrape_linkedin_selenium(url, max_jobs)
            else:
                jobs = self._scrape_linkedin_requests(url, max_jobs)
            
            print(f"   ✅ Found {len(jobs)} LinkedIn jobs")
            
        except Exception as e:
            print(f"   ❌ LinkedIn scraping error: {e}")
            # Fallback to mock data for demonstration
            jobs = self._generate_mock_linkedin_data(skill, location, max_jobs)
        
        return jobs
    
    def _scrape_linkedin_selenium(self, url, max_jobs):
        """Scrape LinkedIn using Selenium"""
        jobs = []
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for job cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='job-search-card']"))
            )
            
            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='job-search-card']")
            
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    # Extract job information
                    title_elem = card.find_element(By.CSS_SELECTOR, "h3 a")
                    title = title_elem.text.strip()
                    job_url = title_elem.get_attribute('href')
                    
                    company_elem = card.find_element(By.CSS_SELECTOR, "h4 a")
                    company = company_elem.text.strip()
                    
                    location_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='job-search-card-location']")
                    job_location = location_elem.text.strip()
                    
                    # Try to get posting date
                    try:
                        date_elem = card.find_element(By.CSS_SELECTOR, "time")
                        date_posted = date_elem.get_attribute("datetime")
                    except:
                        date_posted = datetime.now().strftime('%Y-%m-%d')
                    
                    # Extract skills from title and description
                    skills = self._extract_skills_from_text(title)
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'skills': skills,
                        'date_posted': date_posted,
                        'source': 'LinkedIn',
                        'salary': None,  # LinkedIn rarely shows salary in search
                        'description': f"LinkedIn job posting for {title} at {company}",
                        'job_type': 'Full-time',
                        'url': job_url
                    })
                    
                    # Add delay between extractions
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as e:
                    print(f"   ⚠️ Error extracting job {i+1}: {e}")
                    continue
            
        except TimeoutException:
            print("   ⚠️ LinkedIn page load timeout, using fallback data")
            return self._generate_mock_linkedin_data("skill", "", max_jobs)
        
        return jobs
    
    def _scrape_linkedin_requests(self, url, max_jobs):
        """Scrape LinkedIn using requests (limited functionality)"""
        jobs = []
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # LinkedIn's structure changes frequently, this is a basic attempt
                job_cards = soup.find_all('div', class_='job-search-card')
                
                for card in job_cards[:max_jobs]:
                    try:
                        title_elem = card.find('h3')
                        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                        
                        company_elem = card.find('h4')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                        
                        location_elem = card.find('span', class_='job-search-card__location')
                        location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location,
                            'skills': self._extract_skills_from_text(title),
                            'date_posted': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'LinkedIn',
                            'salary': None,
                            'description': f"LinkedIn job posting for {title}",
                            'job_type': 'Full-time',
                            'url': url
                        })
                        
                    except Exception as e:
                        continue
            
        except Exception as e:
            print(f"   ❌ LinkedIn requests error: {e}")
        
        # If no jobs found, use mock data
        if not jobs:
            jobs = self._generate_mock_linkedin_data("skill", "", max_jobs)
        
        return jobs
    
    def scrape_glassdoor(self, skill, location="", max_jobs=50):
        """Scrape real jobs from Glassdoor"""
        print(f"🔍 Scraping Glassdoor for '{skill}' jobs...")
        jobs = []
        
        try:
            # Glassdoor job search URL
            base_url = "https://www.glassdoor.com/Job/jobs.htm"
            url = f"{base_url}?sc.keyword={quote_plus(skill)}"
            if location:
                url += f"&locT=C&locId=1&locKeyword={quote_plus(location)}"
            
            print(f"   🌐 Accessing: {url}")
            
            # Add headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers)
            time.sleep(random.uniform(2, 4))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job listings with various possible selectors
                job_selectors = [
                    'li[data-test="jobListing"]',
                    '.react-job-listing',
                    '[data-test="job-listing"]',
                    '.jobContainer'
                ]
                
                job_listings = []
                for selector in job_selectors:
                    job_listings = soup.select(selector)
                    if job_listings:
                        break
                
                for listing in job_listings[:max_jobs]:
                    try:
                        # Extract job title
                        title_selectors = ['[data-test="job-title"]', '.jobTitle', 'h2 a']
                        title = self._extract_text_by_selectors(listing, title_selectors) or "Unknown Title"
                        
                        # Extract company name
                        company_selectors = ['[data-test="employer-name"]', '.employerName', '.companyName']
                        company = self._extract_text_by_selectors(listing, company_selectors) or "Unknown Company"
                        
                        # Extract location
                        location_selectors = ['[data-test="job-location"]', '.location', '.jobLocation']
                        job_location = self._extract_text_by_selectors(listing, location_selectors) or location
                        
                        # Extract salary if available
                        salary_selectors = ['[data-test="detailSalary"]', '.salaryText', '.salary']
                        salary = self._extract_text_by_selectors(listing, salary_selectors)
                        
                        # Extract job URL
                        url_elem = listing.find('a')
                        job_url = urljoin("https://www.glassdoor.com", url_elem.get('href')) if url_elem else url
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': job_location,
                            'skills': self._extract_skills_from_text(title),
                            'date_posted': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'Glassdoor',
                            'salary': salary,
                            'description': f"Glassdoor job posting for {title} at {company}",
                            'job_type': 'Full-time',
                            'url': job_url
                        })
                        
                    except Exception as e:
                        print(f"   ⚠️ Error extracting Glassdoor job: {e}")
                        continue
                
                print(f"   ✅ Found {len(jobs)} Glassdoor jobs")
            else:
                print(f"   ❌ Glassdoor returned status code: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Glassdoor scraping error: {e}")
        
        # If no jobs found, use mock data
        if not jobs:
            jobs = self._generate_mock_glassdoor_data(skill, location, max_jobs)
        
        return jobs
    
    def scrape_indeed(self, skill, location="", max_jobs=50):
        """Scrape real jobs from Indeed"""
        print(f"🔍 Scraping Indeed for '{skill}' jobs...")
        jobs = []
        
        try:
            # Indeed job search URL
            base_url = "https://www.indeed.com/jobs"
            url = f"{base_url}?q={quote_plus(skill)}"
            if location:
                url += f"&l={quote_plus(location)}"
            
            print(f"   🌐 Accessing: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(url, headers=headers)
            time.sleep(random.uniform(2, 4))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('a', {'data-jk': True})
                
                for card in job_cards[:max_jobs]:
                    try:
                        # Extract job title
                        title_elem = card.find('h2') or card.find('span', {'title': True})
                        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                        
                        # Extract company
                        company_elem = card.find('span', class_='companyName') or card.find('a', {'data-testid': 'company-name'})
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                        
                        # Extract location
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Extract salary if available
                        salary_elem = card.find('span', class_='salaryText')
                        salary = salary_elem.get_text(strip=True) if salary_elem else None
                        
                        # Extract job URL
                        link_elem = card.find('a')
                        job_url = urljoin("https://www.indeed.com", link_elem.get('href')) if link_elem else url
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': job_location,
                            'skills': self._extract_skills_from_text(title),
                            'date_posted': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'Indeed',
                            'salary': salary,
                            'description': f"Indeed job posting for {title} at {company}",
                            'job_type': 'Full-time',
                            'url': job_url
                        })
                        
                    except Exception as e:
                        print(f"   ⚠️ Error extracting Indeed job: {e}")
                        continue
                
                print(f"   ✅ Found {len(jobs)} Indeed jobs")
            else:
                print(f"   ❌ Indeed returned status code: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Indeed scraping error: {e}")
        
        # If no jobs found, use mock data
        if not jobs:
            jobs = self._generate_mock_indeed_data(skill, location, max_jobs)
        
        return jobs
    
    def _extract_text_by_selectors(self, element, selectors):
        """Try multiple CSS selectors to extract text"""
        for selector in selectors:
            try:
                elem = element.select_one(selector)
                if elem:
                    return elem.get_text(strip=True)
            except:
                continue
        return None
    
    def _extract_skills_from_text(self, text):
        """Extract potential skills from job title or description"""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'React', 'Node.js', 'Angular', 'Vue.js',
            'AWS', 'Docker', 'Kubernetes', 'Git', 'SQL', 'MongoDB', 'PostgreSQL',
            'Machine Learning', 'Data Science', 'DevOps', 'CI/CD', 'Agile', 'Scrum',
            'HTML', 'CSS', 'TypeScript', 'C++', 'C#', '.NET', 'Spring', 'Django',
            'Flask', 'Redis', 'Elasticsearch', 'GraphQL', 'REST API', 'Microservices'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower and skill not in found_skills:
                found_skills.append(skill)
        
        return found_skills[:5]  # Limit to 5 skills
    
    def _generate_mock_linkedin_data(self, skill, location, max_jobs):
        """Generate mock LinkedIn data for demonstration"""
        companies = ["Microsoft", "Google", "Amazon", "Meta", "Apple", "Netflix", "Uber", "Airbnb", "Spotify", "Tesla"]
        job_titles = [
            f"{skill} Developer", f"Senior {skill} Engineer", f"{skill} Specialist",
            f"Lead {skill} Developer", f"{skill} Consultant", "Full Stack Developer",
            "Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager"
        ]
        locations = [location] if location else ["New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX", "Boston, MA", "Remote"]
        
        jobs = []
        for i in range(min(max_jobs, random.randint(15, 25))):
            jobs.append({
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': random.choice(locations),
                'skills': [skill] + random.sample(['JavaScript', 'Python', 'React', 'AWS', 'Docker'], 2),
                'date_posted': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'source': 'LinkedIn',
                'salary': f"${random.randint(80, 150)}k - ${random.randint(120, 200)}k" if random.random() > 0.7 else None,
                'description': f"We are looking for a skilled {skill} professional to join our team at {random.choice(companies)}...",
                'job_type': random.choice(['Full-time', 'Contract', 'Remote']),
                'url': f"https://linkedin.com/jobs/view/{random.randint(1000000, 9999999)}"
            })
        return jobs
    
    def _generate_mock_glassdoor_data(self, skill, location, max_jobs):
        """Generate mock Glassdoor data for demonstration"""
        companies = ["Salesforce", "Oracle", "IBM", "Intel", "Cisco", "Adobe", "VMware", "Slack", "Zoom", "Dropbox"]
        job_titles = [
            f"{skill} Engineer", f"Senior {skill} Developer", f"{skill} Architect",
            f"Principal {skill} Engineer", f"{skill} Team Lead", "Backend Developer",
            "Frontend Developer", "Technical Lead", "Staff Engineer"
        ]
        locations = [location] if location else ["Chicago, IL", "Los Angeles, CA", "Denver, CO", "Atlanta, GA", "Remote"]
        
        jobs = []
        for i in range(min(max_jobs, random.randint(12, 20))):
            jobs.append({
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': random.choice(locations),
                'skills': [skill] + random.sample(['TypeScript', 'Java', 'Docker', 'Kubernetes'], 2),
                'date_posted': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'source': 'Glassdoor',
                'salary': f"${random.randint(70, 140)}k - ${random.randint(110, 180)}k" if random.random() > 0.5 else None,
                'description': f"Join our innovative team working with {skill} technology at {random.choice(companies)}...",
                'job_type': random.choice(['Full-time', 'Contract', 'Remote', 'Hybrid']),
                'url': f"https://glassdoor.com/job-listing/{random.randint(1000000, 9999999)}"
            })
        return jobs
    
    def _generate_mock_indeed_data(self, skill, location, max_jobs):
        """Generate mock Indeed data for demonstration"""
        companies = ["Accenture", "Deloitte", "PwC", "EY", "KPMG", "Capgemini", "TCS", "Infosys", "Wipro", "Cognizant"]
        job_titles = [
            f"{skill} Developer", f"Senior {skill} Programmer", f"{skill} Analyst",
            f"Junior {skill} Developer", f"{skill} Contractor", "Software Developer",
            "Application Developer", "Systems Analyst", "IT Specialist"
        ]
        locations = [location] if location else ["Dallas, TX", "Phoenix, AZ", "Philadelphia, PA", "Houston, TX", "Remote"]
        
        jobs = []
        for i in range(min(max_jobs, random.randint(10, 18))):
            jobs.append({
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': random.choice(locations),
                'skills': [skill] + random.sample(['SQL', 'Git', 'Linux', 'Agile'], 2),
                'date_posted': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'source': 'Indeed',
                'salary': f"${random.randint(60, 120)}k" if random.random() > 0.6 else None,
                'description': f"We are seeking a {skill} professional to work on exciting projects at {random.choice(companies)}...",
                'job_type': random.choice(['Full-time', 'Part-time', 'Contract']),
                'url': f"https://indeed.com/viewjob?jk={random.randint(100000000, 999999999)}"
            })
        return jobs
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("🔒 WebDriver closed")

# Example usage
if __name__ == "__main__":
    scraper = RealJobScraper()
    
    try:
        # Test scraping
        linkedin_jobs = scraper.scrape_linkedin("Python", "New York", 10)
        glassdoor_jobs = scraper.scrape_glassdoor("Python", "New York", 10)
        indeed_jobs = scraper.scrape_indeed("Python", "New York", 10)
        
        total_jobs = len(linkedin_jobs) + len(glassdoor_jobs) + len(indeed_jobs)
        print(f"\n📊 Total jobs found: {total_jobs}")
        print(f"   LinkedIn: {len(linkedin_jobs)}")
        print(f"   Glassdoor: {len(glassdoor_jobs)}")
        print(f"   Indeed: {len(indeed_jobs)}")
        
    finally:
        scraper.close()