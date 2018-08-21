import subprocess
import select
import re

SUMMARY_LINE_REGEX = r'(?P<num_passed>\d+)\spassed\sand\s(?P<num_failed>\d+)\sfailed'
SUMMARY_LINE_PATTERN = re.compile(SUMMARY_LINE_REGEX)

def run_my_tests():
    process = subprocess.Popen(['python', '-m', 'doctest', '-v', 'gogo_scraper.py'], 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()
    output, errors = [line.decode('utf-8') for line in output]
    summary_line = output.split("\n")[-3]
    match = SUMMARY_LINE_PATTERN.search(summary_line)
    if not match:
        errors = "Regex was unable find summary line"
        return (0, 0, errors) 
    return (int(match.group('num_passed')), int(match.group('num_failed')), errors)

if __name__ == '__main__':
    results = run_my_tests()
    print(results)

# 6 passed and 0 failed
