import subprocess
import select
import re

SUMMARY_LINE_REGEX = r'(?P<num_passed>\d+)\spassed\sand\s(?P<num_failed>\d+)\sfailed'
SUMMARY_LINE_PATTERN = re.compile(SUMMARY_LINE_REGEX)

def run_my_doctests():
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


def run_my_unittests():
    process = subprocess.Popen(['python', '-m', 'unittest', '-v', 'test_gogo_scraper.py'], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    _, stdout = process.communicate()
    stdout = stdout.decode("utf-8")
    stdout_lines = stdout.split("\n")
    summary_line = stdout_lines[-2]
    num_of_tests_line = stdout_lines[-4]

    # Line regexes
    num_of_tests_line_pattern = re.compile(r'Ran\s(?P<num_of_tests>\d+)\stests.*')
    summary_line_pattern = re.compile(r'FAILED \(failures=(?P<num_of_failures>\d+)\)')

    summary_match = summary_line_pattern.search(summary_line)
    num_of_tests_match = num_of_tests_line_pattern.search(num_of_tests_line)
    num_of_tests = int(num_of_tests_match.group('num_of_tests'))
    if not summary_match:
        return (num_of_tests,
                0,
                None)

    num_failed = int(summary_match.group("num_of_failures"))
    num_passed = num_of_tests - num_failed

    return (num_passed, num_failed, None)

if __name__ == '__main__':
    results = run_my_unittests()
    print(results)


# 6 passed and 0 failed
