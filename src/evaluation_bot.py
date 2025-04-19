import csv
import os
import datetime
import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse


class AutomatedUsabilityEvaluationBot:
    def _save_experimental_results(self, results, site_name):
        """Save experimental evaluation results to CSV."""
        if not results:
            return

        filename = os.path.join(
            self.output_dir,
            f"experimental_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    )

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["evaluation_type", "user_id", "user_type", "task",
                     "completion_time", "completion_success", "error_count",
                     "action_count", "satisfaction", "difficulty", "comments",
                     "evaluator", "website", "url", "date"]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow(result)

        print(f"Experimental evaluation results saved to {filename}")

    def __init__(self, urls=None):
        self.urls = urls or [
            "https://www.isetcom.tn/public/home.faces",
            "http://www.issatm.rnu.tn/fr/index.php",
            "https://tek-up.de/"
        ]
        self.nielsen_heuristics = [
            "Visibility of System Status",
            "Match Between System and the Real World",
            "User Control and Freedom",
            "Consistency and Standards",
            "Error Prevention",
            "Recognition Rather Than Recall",
            "Flexibility and Efficiency of Use",
            "Aesthetic and Minimalist Design",
            "Help Users Recognize, Diagnose, and Recover from Errors",
            "Help and Documentation"
        ]
        self.bastien_scapin_criteria = [
            "Guidance - Prompting",
            "Guidance - Grouping/Distinction of Items",
            "Guidance - Immediate Feedback",
            "Guidance - Legibility",
            "Workload - Brevity",
            "Workload - Information Density",
            "Explicit Control - Explicit User Action",
            "Explicit Control - User Control",
            "Adaptability - Flexibility",
            "Adaptability - User Experience",
            "Error Management - Error Protection",
            "Error Management - Error Message Quality",
            "Error Management - Error Correction",
            "Consistency",
            "Significance of Codes",
            "Compatibility"
        ]
        self.experimental_metrics = [
            "Task Completion Time",
            "Task Completion Success",
            "Number of Errors",
            "Number of Clicks/Actions",
            "User Satisfaction",
            "Perceived Difficulty",
            "Comments"
        ]
        self.common_tasks = [
            "Find contact information",
            "Search for a specific product",
            "Navigate to About page",
            "Find course information",
            "Locate faculty information",
            "Find admission requirements",
            "Check for news/updates",
            "Find academic calendar",
            "Look for scholarship information",
            "Access student resources"
        ]
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Create output directory
        self.output_dir = "usability_evaluation_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("Automated Usability Evaluation Bot initialized.")

    def run_complete_evaluation(self):
        """Run both heuristic and experimental evaluations for all websites."""
        print("Starting complete automated evaluation...")
        
        for url in self.urls:
            site_name = self._get_site_name(url)
            print(f"\nEvaluating website: {site_name} ({url})")
            
            # Run heuristic evaluation
            print(f"Running heuristic evaluation for {site_name}...")
            nielsen_results = self._run_automated_heuristic_evaluation(url, "Nielsen")
            bastien_results = self._run_automated_heuristic_evaluation(url, "Bastien & Scapin")
            
            # Save heuristic results
            self._save_heuristic_results(nielsen_results, site_name, "Nielsen")
            self._save_heuristic_results(bastien_results, site_name, "Bastien & Scapin")
            
            # Run experimental evaluation
            print(f"Running experimental evaluation for {site_name}...")
            experimental_results = self._run_automated_experimental_evaluation(url)
            
            # Save experimental results
            self._save_experimental_results(experimental_results, site_name)
        
        print("\nEvaluation complete! All results saved to the usability_evaluation_results directory.")

    def _get_site_name(self, url):
        """Extract a clean site name from URL."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        # Remove www. if present and take the next part
        if domain.startswith('www.'):
            domain = domain[4:]
        # Get the main domain name
        return domain.split('.')[0].upper()

    def _run_automated_heuristic_evaluation(self, url, framework):
        """Run automated heuristic evaluation for a website."""
        results = []
        criteria = self.nielsen_heuristics if framework == "Nielsen" else self.bastien_scapin_criteria
        
        try:
            # Set up the browser
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            time.sleep(3)  # Give page time to load
            
            # Get page information
            page_title = driver.title
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyze various aspects of the page
            for criterion in criteria:
                issues, recommendations = self._evaluate_heuristic_criterion(
                    criterion, driver, soup, framework
                )
                
                results.append({
                    "evaluation_type": "heuristic",
                    "framework": framework,
                    "criterion": criterion,
                    "issues": issues,
                    "recommendations": recommendations,
                    "evaluator": "AutomatedBot",
                    "website": self._get_site_name(url),
                    "url": url,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
            
            driver.quit()
            
        except Exception as e:
            print(f"Error during heuristic evaluation: {e}")
            # Add error to results
            results.append({
                "evaluation_type": "heuristic",
                "framework": framework,
                "criterion": "ERROR",
                "issues": f"Failed to evaluate: {str(e)}",
                "recommendations": "Check website accessibility",
                "evaluator": "AutomatedBot",
                "website": self._get_site_name(url),
                "url": url,
                "date": datetime.datetime.now().strftime("%Y-%m-%d")
            })
        
        return results

    def _evaluate_heuristic_criterion(self, criterion, driver, soup, framework):
        """Evaluate a specific heuristic criterion."""
        issues = []
        recommendations = []
        
        # Visibility of System Status
        if criterion == "Visibility of System Status" or criterion == "Guidance - Immediate Feedback":
            # Check for loading indicators
            loading_indicators = soup.find_all(class_=lambda c: c and ('load' in c.lower() or 'spinner' in c.lower() or 'progress' in c.lower()))
            if not loading_indicators:
                issues.append("No visible loading indicators found")
                recommendations.append("Add loading indicators to show system status during operations")
            
            # Check for form feedback
            forms = soup.find_all('form')
            for form in forms:
                if not form.find_all(['input', 'select', 'textarea']):
                    continue
                submit_btn = form.find(['button', 'input'], {'type': 'submit'})
                if submit_btn and not any('success' in str(c).lower() or 'error' in str(c).lower() for c in form.find_all(class_=True)):
                    issues.append("Forms may lack immediate feedback after submission")
                    recommendations.append("Add visual feedback for form submissions")
        
        # Match Between System and the Real World
        elif criterion == "Match Between System and the Real World" or criterion == "Compatibility":
            # Check for technical jargon in text content
            text_content = soup.get_text()
            technical_terms = ['404', 'runtime', 'backend', 'frontend', 'api', 'json', 'http']
            found_jargon = [term for term in technical_terms if term in text_content.lower()]
            if found_jargon:
                issues.append(f"Technical jargon found: {', '.join(found_jargon)}")
                recommendations.append("Replace technical terms with user-friendly language")
            
            # Check if icons match conventional meanings
            icons = soup.find_all('i', class_=True)
            unconventional_icons = []
            for icon in icons:
                icon_classes = icon.get('class', [])
                class_str = ' '.join(icon_classes).lower()
                if ('search' in class_str and not ('magnify' in class_str or 'glass' in class_str)) or \
                   ('home' in class_str and not ('house' in class_str)) or \
                   ('cart' in class_str and not ('shop' in class_str or 'basket' in class_str)):
                    unconventional_icons.append(str(icon_classes))
            
            if unconventional_icons:
                issues.append(f"Potentially unconventional icon usage")
                recommendations.append("Ensure icons follow standard conventions")
        
        # User Control and Freedom
        elif criterion == "User Control and Freedom" or criterion == "Explicit Control - User Control":
            # Check for cancel/back options
            forms = soup.find_all('form')
            for form in forms:
                has_cancel = bool(form.find(['button', 'a', 'input'], text=lambda t: t and ('cancel' in t.lower() or 'back' in t.lower())))
                has_reset = bool(form.find(['button', 'input'], {'type': 'reset'}))
                if not (has_cancel or has_reset):
                    issues.append("Forms lack cancel/back options")
                    recommendations.append("Add cancel and back buttons to forms")
            
            # Check for exit points from processes
            multi_step_indicators = soup.find_all(class_=lambda c: c and ('step' in c.lower() or 'wizard' in c.lower() or 'progress' in c.lower()))
            if multi_step_indicators and not soup.find_all(['a', 'button'], text=lambda t: t and ('exit' in t.lower() or 'cancel' in t.lower())):
                issues.append("Multi-step processes lack exit points")
                recommendations.append("Add exit options for multi-step processes")
        
        # Consistency and Standards
        elif criterion == "Consistency and Standards" or criterion == "Consistency":
            # Check for consistent button styling
            buttons = soup.find_all(['button', 'a'], class_=True)
            button_classes = [' '.join(b.get('class', [])) for b in buttons]
            if len(set(button_classes)) > 3 and len(buttons) > 5:  # If more than 3 different button styles
                issues.append("Inconsistent button styling")
                recommendations.append("Standardize button styles throughout the interface")
            
            # Check for consistent header structure
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            header_structure = {}
            for h in headers:
                tag_name = h.name
                if tag_name not in header_structure:
                    header_structure[tag_name] = 0
                header_structure[tag_name] += 1
            
            # Check if headers are used in a logical order
            header_levels = sorted(header_structure.keys(), key=lambda x: int(x[1]))
            for i, level in enumerate(header_levels[:-1]):
                next_level = header_levels[i+1]
                if int(next_level[1]) - int(level[1]) > 1:
                    issues.append(f"Inconsistent header structure: jumped from {level} to {next_level}")
                    recommendations.append("Maintain logical header hierarchy")
        
        # Error Prevention
        elif criterion == "Error Prevention" or criterion == "Error Management - Error Protection":
            # Check for required fields in forms
            forms = soup.find_all('form')
            for form in forms:
                required_inputs = form.find_all(['input', 'select', 'textarea'], {'required': True})
                if not required_inputs and form.find_all(['input', 'select', 'textarea']):
                    issues.append("Forms may lack required field validation")
                    recommendations.append("Add required field validation to prevent submission errors")
            
            # Check for input type validation
            forms = soup.find_all('form')
            for form in forms:
                email_inputs = form.find_all('input', {'type': 'email'})
                if not email_inputs and form.find_all('input', text=lambda t: t and 'email' in t.lower()):
                    issues.append("Email fields may lack type validation")
                    recommendations.append("Use appropriate input types (email, tel, number) for validation")
        
        # Recognition Rather Than Recall
        elif criterion == "Recognition Rather Than Recall" or criterion == "Workload - Information Density":
            # Check for labeled form fields
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'select', 'textarea'])
                for input_field in inputs:
                    input_id = input_field.get('id')
                    if input_id and not form.find('label', {'for': input_id}):
                        input_placeholder = input_field.get('placeholder')
                        if not input_placeholder:
                            issues.append("Form fields lack proper labels")
                            recommendations.append("Add descriptive labels to all form fields")
                            break
            
            # Check for visible navigation cues
            nav = soup.find('nav') or soup.find(class_=lambda c: c and 'nav' in c.lower())
            if nav:
                active_indicators = nav.find_all(class_=lambda c: c and 'active' in c.lower())
                if not active_indicators:
                    issues.append("Navigation may lack indicators for current location")
                    recommendations.append("Add 'active' state indicators to navigation items")
        
        # Flexibility and Efficiency of Use
        elif criterion == "Flexibility and Efficiency of Use" or criterion == "Adaptability - Flexibility":
            # Check for keyboard shortcuts
            if not soup.find_all('kbd') and not soup.find_all(attrs={'accesskey': True}):
                issues.append("No keyboard shortcuts found")
                recommendations.append("Implement keyboard shortcuts for common actions")
            
            # Check for search functionality
            search_elements = soup.find_all(['input', 'form'], {'type': 'search'}) or \
                            soup.find_all(['input', 'form'], {'name': lambda n: n and 'search' in n.lower()}) or \
                            soup.find_all(class_=lambda c: c and 'search' in c.lower())
            if not search_elements:
                issues.append("No search functionality found")
                recommendations.append("Add search functionality for quick access to content")
        
        # Aesthetic and Minimalist Design
        elif criterion == "Aesthetic and Minimalist Design" or criterion == "Workload - Brevity":
            # Check for content density
            paragraphs = soup.find_all('p')
            avg_length = sum(len(p.get_text()) for p in paragraphs) / max(len(paragraphs), 1)
            if avg_length > 200:
                issues.append(f"Content may be too dense (avg paragraph length: {avg_length:.0f} chars)")
                recommendations.append("Break up long text into shorter, more digestible segments")
            
            # Check for excessive UI elements
            total_elements = len(soup.find_all(True))
            if total_elements > 500:
                issues.append(f"Interface may be too complex ({total_elements} elements)")
                recommendations.append("Simplify interface by removing unnecessary elements")
        
        # Help Users Recognize, Diagnose, and Recover from Errors
        elif criterion == "Help Users Recognize, Diagnose, and Recover from Errors" or criterion == "Error Management - Error Message Quality":
            # Check for error message styling
            error_messages = soup.find_all(class_=lambda c: c and 'error' in c.lower()) or \
                            soup.find_all(class_=lambda c: c and 'alert' in c.lower() and 'danger' in c.lower())
            if not error_messages:
                issues.append("No styled error messages found")
                recommendations.append("Add clear visual styling to error messages")
            
            # Check for error instructions
            if error_messages:
                helpful_errors = 0
                for error in error_messages:
                    text = error.get_text().lower()
                    if any(phrase in text for phrase in ['try', 'please', 'should', 'must', 'can']):
                        helpful_errors += 1
                
                if helpful_errors < len(error_messages) / 2:
                    issues.append("Error messages may lack helpful instructions")
                    recommendations.append("Include specific guidance in error messages")
        
        # Help and Documentation
        elif criterion == "Help and Documentation":
            # Check for help/FAQ sections
            help_links = soup.find_all(['a', 'button'], text=lambda t: t and any(word in t.lower() for word in ['help', 'faq', 'support', 'guide', 'documentation']))
            if not help_links:
                issues.append("No help or documentation links found")
                recommendations.append("Add easily accessible help and FAQ sections")
            
            # Check for contextual help
            forms = soup.find_all('form')
            for form in forms:
                help_text = form.find_all(class_=lambda c: c and any(word in c.lower() for word in ['help', 'hint', 'info', 'tooltip']))
                if not help_text and len(form.find_all(['input', 'select', 'textarea'])) > 2:
                    issues.append("Forms lack contextual help")
                    recommendations.append("Add tooltips or help text to complex form fields")
                    break
        
        # For the remaining Bastien & Scapin criteria not directly mapped to Nielsen
        elif framework == "Bastien & Scapin":
            # Guidance - Prompting
            if criterion == "Guidance - Prompting":
                # Check for clear calls to action
                buttons = soup.find_all(['button', 'input'], {'type': ['submit', 'button']})
                vague_buttons = [b for b in buttons if b.get_text().strip() in ['Submit', 'Click', 'Go', '']]
                if vague_buttons:
                    issues.append("Vague call-to-action buttons found")
                    recommendations.append("Use specific action verbs on buttons")
            
            # Guidance - Grouping/Distinction of Items
            elif criterion == "Guidance - Grouping/Distinction of Items":
                # Check for logical grouping of elements
                forms = soup.find_all('form')
                for form in forms:
                    fieldsets = form.find_all('fieldset')
                    if not fieldsets and len(form.find_all(['input', 'select', 'textarea'])) > 5:
                        issues.append("Form elements may not be properly grouped")
                        recommendations.append("Use fieldsets to group related form elements")
                        break
            
            # Guidance - Legibility
            elif criterion == "Guidance - Legibility":
                # Check for text contrast (simplified)
                text_elements = soup.find_all(['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                has_light_text = any('light' in ' '.join(el.get('class', [])).lower() for el in text_elements)
                if has_light_text:
                    issues.append("Potentially low-contrast text found")
                    recommendations.append("Ensure sufficient contrast between text and background")
            
            # Explicit Control - Explicit User Action
            elif criterion == "Explicit Control - Explicit User Action":
                # Check for auto-playing elements
                auto_elements = soup.find_all(['video', 'audio'], {'autoplay': True})
                if auto_elements:
                    issues.append("Auto-playing media elements found")
                    recommendations.append("Avoid auto-playing media; let users control playback")
            
            # Adaptability - User Experience
            elif criterion == "Adaptability - User Experience":
                # Check for responsive design
                viewport_meta = soup.find('meta', {'name': 'viewport'})
                if not viewport_meta or 'width=device-width' not in viewport_meta.get('content', ''):
                    issues.append("May not be optimized for mobile devices")
                    recommendations.append("Implement responsive design with appropriate viewport meta tag")
            
            # Error Management - Error Correction
            elif criterion == "Error Management - Error Correction":
                # Check for form field persistence
                forms = soup.find_all('form')
                for form in forms:
                    if form.get('method', '').lower() == 'get' and not form.find('input', {'type': 'hidden', 'name': 'form_state'}):
                        issues.append("Forms may not preserve data on error")
                        recommendations.append("Implement form state preservation for error correction")
                        break
            
            # Significance of Codes
            elif criterion == "Significance of Codes":
                # Check for icon text alternatives
                icons = soup.find_all('i', class_=lambda c: c and any(word in c for word in ['icon', 'fa-', 'material-icons']))
                for icon in icons:
                    if not icon.get('aria-label') and not icon.get('title'):
                        issues.append("Icons lack meaningful labels")
                        recommendations.append("Add aria-label or title attributes to icons")
                        break
        
        # Default case
        if not issues:
            issues.append(f"No automated issues detected for {criterion}")
            recommendations.append("Consider manual review for this criterion")
        
        return "; ".join(issues), "; ".join(recommendations)

    def _run_automated_experimental_evaluation(self, url):
        """Simulate experimental evaluation with virtual users."""
        results = []
        tasks = self._generate_tasks_for_site(url)
        user_types = ["Expert", "First-time user"]
        
        # Simulate 5 users per type
        for user_type in user_types:
            for user_num in range(1, 6):
                user_id = f"{user_type[0]}{user_num}"  # E1, E2, F1, F2, etc.
                
                for task in tasks:
                    # Simulate task performance metrics
                    metrics = self._simulate_user_performance(task, user_type)
                    
                    results.append({
                        "evaluation_type": "experimental",
                        "user_id": user_id,
                        "user_type": user_type,
                        "task": task,
                        "completion_time": metrics["completion_time"],
                        "completion_success": metrics["completion_success"],
                        "error_count": metrics["error_count"],
                        "action_count": metrics["action_count"],
                        "satisfaction": metrics["satisfaction"],
                        "difficulty": metrics["difficulty"],
                        "comments": metrics["comments"],
                        "evaluator": "AutomatedBot",
                        "website": self._get_site_name(url),
                        "url": url,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d")
                    })
        
        return results

    def _generate_tasks_for_site(self, url):
        """Generate appropriate tasks based on website type."""
        site_name = self._get_site_name(url)
        
        # Default tasks that work for educational websites
        tasks = [
            f"Find contact information for {site_name}",
            f"Search for a specific course on the {site_name} website",
            f"Find information about admission requirements at {site_name}",
            f"Locate the faculty directory on the {site_name} website",
            f"Find the academic calendar on the {site_name} website",
            f"Locate student resources on the {site_name} website"
        ]
        
        # Use a subset of tasks (at least 4)
        return random.sample(tasks, min(4, len(tasks)))

    def _simulate_user_performance(self, task, user_type):
        """Simulate user performance for a given task."""
        # Base metrics
        base_metrics = {
            "Expert": {
                "completion_time": (5, 45),  # Range in seconds
                "error_chance": 0.2,
                "error_count": (0, 2),
                "action_count": (3, 10),
                "satisfaction": (3, 5),
                "difficulty": (1, 3)
            },
            "First-time user": {
                "completion_time": (30, 120),
                "error_chance": 0.7,
                "error_count": (1, 5),
                "action_count": (7, 20),
                "satisfaction": (2, 4),
                "difficulty": (2, 5)
            }
        }
        
        metrics = base_metrics[user_type]
        
        # Task complexity factor (some tasks are harder)
        complexity = 1.0
        if "search" in task.lower():
            complexity = 1.2
        elif "find" in task.lower() and "faculty" in task.lower():
            complexity = 1.3
        elif "admission" in task.lower():
            complexity = 1.1
        
        # Success determined by task complexity and user type
        success_chance = 0.95 if user_type == "Expert" else 0.75
        success_chance /= complexity
        success = random.random() < success_chance
        
        # Generate metrics
        completion_time = int(random.uniform(metrics["completion_time"][0], 
                                             metrics["completion_time"][1]) * complexity)
        
        if not success:
            completion_time *= 1.5  # Failed tasks take longer
        
        had_errors = random.random() < metrics["error_chance"]
        error_count = random.randint(metrics["error_count"][0], metrics["error_count"][1]) if had_errors else 0
        
        if not success:
            error_count += random.randint(1, 3)  # Failed tasks have more errors
        
        action_count = random.randint(metrics["action_count"][0], metrics["action_count"][1])
        if not success:
            action_count *= 1.5  # Failed tasks have more actions
        action_count = int(action_count)
        
        satisfaction = random.randint(metrics["satisfaction"][0], metrics["satisfaction"][1])
        if not success:
            satisfaction = max(1, satisfaction - 2)  # Lower satisfaction on failure
        
        difficulty = random.randint(metrics["difficulty"][0], metrics["difficulty"][1])
        if not success:
            difficulty = min(5, difficulty + 2)  # Higher difficulty on failure
            
        # Generate appropriate comments
        comments = self._generate_user_comment(task, user_type, success, error_count, difficulty)
        
        return {
            "completion_time": completion_time,
            "completion_success": "Y" if success else "N",
            "error_count": error_count,
            "action_count": action_count,
            "satisfaction": satisfaction,
            "difficulty": difficulty,
            "comments": comments
        }

    def _generate_user_comment(self, task, user_type, success, error_count, difficulty):
        """Generate a realistic user comment based on task performance."""
        comments = []
        
        # Success comments
        success_comments = [
            "I completed the task without any issues.",
            "The interface was straightforward for this task.",
            "This was easy to accomplish.",
            "Found what I needed quickly.",
            "The website made this task simple."
        ]
        
        # Difficulty comments
        difficulty_comments = [
            "This was quite challenging to complete.",
            "I struggled to find the right section.",
            "The navigation was confusing for this task.",
            "Had trouble understanding where to look.",
            "The website organization made this difficult."
        ]
        
        # Error comments
        error_comments = [
            "I made several mistakes while trying to complete this.",
            "Clicked on the wrong sections multiple times.",
            "Kept getting lost in the website structure.",
            "The labeling was misleading and caused errors.",
            "Had to backtrack several times."
        ]
        
        # Expert-specific comments
        expert_comments = [
            "As someone familiar with these sites, I expected to find this in the main menu.",
            "The site doesn't follow standard conventions for this function.",
            "Most similar websites place this in a more accessible location.",
            "Could be improved by following industry standards.",
            "The site structure differs from what I'm used to."
        ]
        
        # First-time user comments
        novice_comments = [
            "As a first-time visitor, I wasn't sure where to start.",
            "The terminology used was unfamiliar to me.",
            "I had to explore multiple sections before finding the right one.",
            "Would benefit from clearer instructions for new users.",
            "The layout wasn't intuitive for someone unfamiliar with the site."
        ]
        
        # Build comment based on performance
        if success and difficulty <= 2:
            comments.append(random.choice(success_comments))
        elif success and difficulty > 2:
            comments.append("Completed the task, but " + random.choice(difficulty_comments).lower())
        else:
            comments.append("Couldn't complete the task. " + random.choice(difficulty_comments))
        
        if error_count > 2:
            comments.append(random.choice(error_comments))
        
        # Add user type specific comment
        if user_type == "Expert":
            comments.append(random.choice(expert_comments))
        else:
            comments.append(random.choice(novice_comments))
        
        # Add task-specific comment
        if "contact" in task.lower():
            comments.append("Contact information " + ("was easy to find." if success else "was hard to locate."))
        elif "search" in task.lower():
            comments.append("The search functionality " + ("worked well." if success else "was not intuitive."))
        elif "admission" in task.lower():
            comments.append("Admission requirements " + ("were clearly presented." if success else "were scattered across multiple pages."))
        
        return " ".join(comments)

    def _save_heuristic_results(self, results, site_name, framework):
        """Save heuristic evaluation results to CSV."""
        if not results:
            return
        
        filename = os.path.join(
            self.output_dir, 
            f"heuristic_{framework.replace(' & ', '_')}_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["evaluation_type", "framework", "criterion", "issues", 
                         "recommendations", "evaluator", "website", "url", "date"]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow(result)
        
        print(f"Heuristic evaluation results saved to {filename}")

def _save_experimental_results(self, results, site_name):
    """Save experimental evaluation results to CSV."""
    if not results:
        return
    
    filename = os.path.join(
        self.output_dir, 
        f"experimental_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    )
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["evaluation_type", "user_id", "user_type", "task", 
                     "completion_time", "completion_success", "error_count", 
                     "action_count", "satisfaction", "difficulty", "comments", 
                     "evaluator", "website", "url", "date"]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
    
    print(f"Experimental evaluation results saved to {filename}")



def generate_summary_report():
    """Generate a summary report of all evaluations."""
    print("\nGenerating summary report...")
    
    report_filename = os.path.join(
        self.output_dir,
        f"summary_report_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
    )
    
    with open(report_filename, 'w', encoding='utf-8') as report_file:
        report_file.write("AUTOMATED USABILITY EVALUATION SUMMARY REPORT\n")
        report_file.write("=" * 50 + "\n\n")
        report_file.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for url in self.urls:
            site_name = self._get_site_name(url)
            report_file.write(f"\nWEBSITE: {site_name} ({url})\n")
            report_file.write("-" * 50 + "\n\n")
            
            # Summarize heuristic evaluations
            report_file.write("HEURISTIC EVALUATION SUMMARY:\n\n")
            
            # Look for Nielsen results
            nielsen_file = os.path.join(
                self.output_dir, 
                f"heuristic_Nielsen_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if os.path.exists(nielsen_file):
                report_file.write("Nielsen's Heuristics - Top Issues:\n")
                
                with open(nielsen_file, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if "No automated issues detected" not in row['issues']:
                            report_file.write(f"- {row['criterion']}: {row['issues']}\n")
                            report_file.write(f"  Recommendation: {row['recommendations']}\n\n")
            
            # Look for Bastien & Scapin results
            bastien_file = os.path.join(
                self.output_dir, 
                f"heuristic_Bastien_Scapin_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if os.path.exists(bastien_file):
                report_file.write("Bastien & Scapin's Criteria - Top Issues:\n")
                
                with open(bastien_file, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if "No automated issues detected" not in row['issues']:
                            report_file.write(f"- {row['criterion']}: {row['issues']}\n")
                            report_file.write(f"  Recommendation: {row['recommendations']}\n\n")
            
            # Summarize experimental evaluations
            exp_file = os.path.join(
                self.output_dir, 
                f"experimental_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if os.path.exists(exp_file):
                report_file.write("\nEXPERIMENTAL EVALUATION SUMMARY:\n\n")
                
                # Calculate metrics
                success_rates = {"Expert": [], "First-time user": []}
                completion_times = {"Expert": [], "First-time user": []}
                error_counts = {"Expert": [], "First-time user": []}
                difficulty_ratings = {"Expert": [], "First-time user": []}
                
                with open(exp_file, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        user_type = row['user_type']
                        success_rates[user_type].append(1 if row['completion_success'] == 'Y' else 0)
                        completion_times[user_type].append(int(row['completion_time']))
                        error_counts[user_type].append(int(row['error_count']))
                        difficulty_ratings[user_type].append(int(row['difficulty']))
                
                # Report metrics
                for user_type in ["Expert", "First-time user"]:
                    if success_rates[user_type]:
                        avg_success = sum(success_rates[user_type]) / len(success_rates[user_type]) * 100
                        avg_time = sum(completion_times[user_type]) / len(completion_times[user_type])
                        avg_errors = sum(error_counts[user_type]) / len(error_counts[user_type])
                        avg_difficulty = sum(difficulty_ratings[user_type]) / len(difficulty_ratings[user_type])
                        
                        report_file.write(f"{user_type} Users:\n")
                        report_file.write(f"- Success Rate: {avg_success:.1f}%\n")
                        report_file.write(f"- Average Completion Time: {avg_time:.1f} seconds\n")
                        report_file.write(f"- Average Error Count: {avg_errors:.1f}\n")
                        report_file.write(f"- Average Difficulty Rating: {avg_difficulty:.1f}/5\n\n")
            
            # Add recommendations
            report_file.write("\nKEY RECOMMENDATIONS:\n\n")
            
            # Collect all issues
            all_issues = []
            for filename in os.listdir(self.output_dir):
                if filename.startswith(f"heuristic_") and site_name in filename:
                    with open(os.path.join(self.output_dir, filename), 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if "No automated issues detected" not in row['issues']:
                                all_issues.append({
                                    'criterion': row['criterion'],
                                    'issues': row['issues'],
                                    'recommendations': row['recommendations']
                                })
            
            # Prioritize top 5 issues
            if all_issues:
                # Simple prioritization based on issue frequency
                issue_count = {}
                for issue in all_issues:
                    key_issues = issue['issues'].split(';')
                    for ki in key_issues:
                        ki = ki.strip()
                        if ki not in issue_count:
                            issue_count[ki] = {'count': 0, 'recommendation': ''}
                        issue_count[ki]['count'] += 1
                        issue_count[ki]['recommendation'] = issue['recommendations']
                
                # Select top 5 issues
                top_issues = sorted(issue_count.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
                
                for i, (issue, data) in enumerate(top_issues, 1):
                    report_file.write(f"{i}. {issue}\n   Recommendation: {data['recommendation']}\n\n")
            else:
                report_file.write("No significant issues detected.\n")
        
        report_file.write("\n\nENVIRONMENT INFORMATION:\n")
        report_file.write(f"Evaluation Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        report_file.write("Evaluation Tool: Automated Usability Evaluation Bot\n")
    
    print(f"Summary report generated: {report_filename}")




def visualize_results(self):
        """Create visualizations of the evaluation results."""
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            import numpy as np
        except ImportError:
            print("Visualization libraries not available. Skipping visualization.")
            return

        print("\nGenerating visualizations...")

        # Create visualization directory
        viz_dir = os.path.join(self.output_dir, "visualizations")
        os.makedirs(viz_dir, exist_ok=True)

        for url in self.urls:
            site_name = self._get_site_name(url)

            # Visualize experimental results
            exp_file = os.path.join(
                self.output_dir,
                f"experimental_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            )

            if os.path.exists(exp_file):
                # Load data
                exp_data = pd.read_csv(exp_file)

                # Success rates by user type
                plt.figure(figsize=(10, 6))
                success_rates = exp_data.groupby(['user_type', 'task'])['completion_success'].apply(
                    lambda x: (x == 'Y').mean() * 100
                ).unstack()

                success_rates.plot(kind='bar')
                plt.title(f'Task Success Rates by User Type - {site_name}')
                plt.ylabel('Success Rate (%)')
                plt.xlabel('User Type')
                plt.xticks(rotation=0)
                plt.ylim(0, 100)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, f"{site_name}_success_rates.png"))

                # Completion times by user type
                plt.figure(figsize=(10, 6))
                times = exp_data.groupby(['user_type', 'task'])['completion_time'].mean().unstack()
                times.plot(kind='bar')
                plt.title(f'Average Task Completion Time by User Type - {site_name}')
                plt.ylabel('Time (seconds)')
                plt.xlabel('User Type')
                plt.xticks(rotation=0)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, f"{site_name}_completion_times.png"))

                # User satisfaction and difficulty
                plt.figure(figsize=(10, 6))
                metrics = exp_data.groupby('user_type')[['satisfaction', 'difficulty']].mean()
                metrics.plot(kind='bar')
                plt.title(f'User Experience Metrics - {site_name}')
                plt.ylabel('Average Rating (1-5)')
                plt.xlabel('User Type')
                plt.xticks(rotation=0)
                plt.ylim(0, 5)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, f"{site_name}_user_experience.png"))

            # Visualize heuristic results
            nielsen_file = os.path.join(
                self.output_dir,
                f"heuristic_Nielsen_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            )

            bastien_file = os.path.join(
                self.output_dir,
                f"heuristic_Bastien_Scapin_{site_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            )

            if os.path.exists(nielsen_file) and os.path.exists(bastien_file):
                # Load data
                nielsen_data = pd.read_csv(nielsen_file)
                bastien_data = pd.read_csv(bastien_file)

                # Count issues by criterion
                nielsen_issues = nielsen_data.apply(
                    lambda row: 0 if "No automated issues detected" in row['issues'] else len(row['issues'].split(';')),
                    axis=1
                )

                bastien_issues = bastien_data.apply(
                    lambda row: 0 if "No automated issues detected" in row['issues'] else len(row['issues'].split(';')),
                    axis=1
                )

                # Create a horizontal bar chart for Nielsen heuristics
                plt.figure(figsize=(12, 8))
                y_pos = np.arange(len(nielsen_data['criterion']))
                plt.barh(y_pos, nielsen_issues)
                plt.yticks(y_pos, nielsen_data['criterion'])
                plt.xlabel('Number of Issues')
                plt.title(f'Nielsen Heuristic Issues - {site_name}')
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, f"{site_name}_nielsen_issues.png"))


                # Create a horizontal bar chart for Bastien & Scapin criteria
                plt.figure(figsize=(14, 10))
                y_pos = np.arange(len(bastien_data['criterion']))
                plt.barh(y_pos, bastien_issues)
                plt.yticks(y_pos, bastien_data['criterion'])
                plt.xlabel('Number of Issues')
                plt.title(f'Bastien & Scapin Criteria Issues - {site_name}')
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, f"{site_name}_bastien_issues.png"))

        print(f"Visualizations saved to {viz_dir}")


def main():
    """Main function to run the usability evaluation bot."""
    print("=" * 50)
    print("AUTOMATED USABILITY EVALUATION BOT")
    print("=" * 50)
    print("\nThis bot evaluates website usability using:")
    print("1. Heuristic evaluation (Nielsen's 10 heuristics & Bastien-Scapin criteria)")
    print("2. Simulated experimental user testing")

    # Default URLs to evaluate
    default_urls = [
        "https://www.isetcom.tn/public/home.faces",
        "http://www.issatm.rnu.tn/fr/index.php",
        "https://tek-up.de/"
    ]

    # Ask if user wants to use custom URLs
    use_custom = input("\nDo you want to evaluate custom URLs? (y/n, default: n): ").lower() == 'y'

    if use_custom:
        custom_urls = []
        print("\nEnter URLs to evaluate (one per line, empty line to finish):")
        while True:
            url = input("> ").strip()
            if not url:
                break
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'https://' + url
            custom_urls.append(url)

        if custom_urls:
            bot = AutomatedUsabilityEvaluationBot(urls=custom_urls)
        else:
            print("No URLs entered. Using default URLs.")
            bot = AutomatedUsabilityEvaluationBot()
    else:
        bot = AutomatedUsabilityEvaluationBot()

    # Run the evaluations
    bot.run_complete_evaluation()

    # Generate summary report
    bot.generate_summary_report()

    # Ask if user wants visualizations
    if input("\nGenerate visualizations? (y/n, default: y): ").lower() != 'n':
        bot.visualize_results()

    print("\n" + "=" * 50)
    print("EVALUATION COMPLETE")
    print("=" * 50)
    print(f"\nAll results saved to the {bot.output_dir} directory.")


if __name__ == "__main__":
    main()
