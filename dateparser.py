
import dateparser

# List of example date strings with OCR issues and typos

# Extracting standard dates using dateparser
#extracted_dates = [dateparser.parse(date_string) for date_string in date_strings]

# Printing the results
#for original, extracted in zip(date_strings, extracted_dates):
#    print(f"Original: {original} => Extracted: {extracted}")


# #date_string = [
#     "2023-13-01", "20th of June, 2023", "Februarv 29, 2024", "31/04/2023", "Marh 5, 2023",
#     "202/06/15", "20/15/2023", "1st of Jan, 2023", "July 32, 2023", "2022-12-32",
#     "13th of Dec, 2023", "2024/02/29", "30th Feb 2020", "2021-04-31", "Apri1 5, 2023",
#     "Decemher 12, 2023", "2023-11-3O", "01/01/2022", "Sept 31, 2023", "Feb 30, 2024",
#     "2022-06-31", "Nov 31, 2023", "20th Jan 2024", "32/01/2023", "2023-00-15",
#     "31/02/2024", "Apr 31, 2023", "Octobe 10, 2022", "30th Jun 2023", "05/13/2023",
#     "Juli 4, 2023", "202-04-15", "2024-02-30", "13/13/2023", "Augus 15, 2023",
#     "31/06/2022", "Feb 29, 2021", "Septmber 5, 2023", "04-31-2023", "15/15/2023",
#     "March 32, 2023", "2022-14-01", "Janyary 1, 2023", "30th Feb 2023", "2020-11-31",
#     "31-09-2023", "Febuary 28, 2024", "2023-02-29", "Juli 30, 2023", "2021/13/01"
#  ----------------------------------------------------------------

import re 
from fuzzywuzzy import process

class SimpleCorrection:
    def __init__(self, use_fuzzy_matching=False, fuzzy_threshold=80):
        self.correction_dict = {}
        self.use_fuzzy_matching = use_fuzzy_matching
        self.fuzzy_threshold = fuzzy_threshold
    
    def add_correction(self, typo, correct):
        """Add a specific typo correction to the dictionary."""
        self.correction_dict[typo.lower()] = correct
    
    def correct_string(self, input_string):
        """Correct known typos in a string using the correction dictionary."""
        for typo, correct in self.correction_dict.items():
            input_string = re.sub(rf'\b{typo}\b', correct, input_string, flags=re.IGNORECASE)
        return input_string
    
    def correct_w_fuzzy(self, word, valid_words):
        """Use fuzzy matching to correct a word against a list of valid words."""
        match, score = process.extractOne(word, valid_words)
        return match if score >= self.fuzzy_threshold else word
    
    def remove_suffix(self, word):
        """Remove common suffixes like 'th', 'st', 'nd', 'rd' from date numbers."""
        return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', word, flags=re.IGNORECASE)
    
    def remove_of(self, date_string):
        """Remove the word 'of' from phrases like '25th of July'."""
        return re.sub(r'(\d+)(st|nd|rd|th)?\s+of\s+([A-Za-z]+)', r'\1 \3', date_string, flags=re.IGNORECASE)
    
    def reorder_date(self, date_string):
        """Reorder date parts if necessary."""
        # Match patterns like '25th July, 2022' or '25 July 2022'
        match = re.match(r'(\d+)(?:st|nd|rd|th)?\s+([A-Za-z]+),?\s*(\d{4})', date_string)
        if match:
            day, month, year = match.groups()
            return f"{month} {day}, {year}"
        return date_string
    
    def correct(self, date_string):
        """Apply all correction strategies to the input string."""
        # Step 1: Remove 'of' where applicable
        date_string = self.remove_of(date_string)
        
        words = date_string.split()
        valid_months = ["January", "February", "March", "April", "May", "June", 
                        "July", "August", "September", "October", "November", "December"]
        
        corrected_words = []
        
        for word in words:
            # Step 2: Remove 'th', 'st', 'nd', 'rd' suffixes if present
            word = self.remove_suffix(word)
            
            # Step 3: Correct with known typos
            corrected_word = self.correct_string(word)
            
            # Step 4: If the word still appears incorrect and fuzzy matching is enabled, try fuzzy matching
            if self.use_fuzzy_matching and corrected_word.lower() not in valid_months:
                corrected_word = self.correct_w_fuzzy(corrected_word, valid_months)
            
            corrected_words.append(corrected_word)
        
        # Step 5: Reorder the date parts if necessary
        corrected_date = ' '.join(corrected_words)
        return self.reorder_date(corrected_date)

# Adding test cases:
correction_engine = SimpleCorrection(use_fuzzy_matching=True)
correction_engine.add_correction("Marh", "March")
correction_engine.add_correction("Apri1", "April")
correction_engine.add_correction("Decemher", "December")

date_strings = ["Marh 5, 2023", "Octobe 10, 2022", "Augus 15, 2023", "Apri1 5, 2023", "Decemher 12, 2023","25th of July, 2022","10 Apr 2024", "Apr 10th, 2024", "5 May 2024"]

for item in date_strings: 
    corrected_string = correction_engine.correct(item) 
    print(f"Original: {item} => Corrected: {corrected_string}")
