import subprocess
import sys
import os

def run_pytest_with_coverage():
    run_cov = subprocess.run(
        [sys.executable, '-m', 'coverage', 'run', '-m', 'pytest'],
        capture_output=True,
        text=True
    )
    print(run_cov.stdout)
    if run_cov.returncode != 0:
        print(run_cov.stderr, file=sys.stderr)
        sys.exit(run_cov.returncode)
    
    gen_html = subprocess.run(
        [sys.executable, '-m', 'coverage', 'html'],
        capture_output=True,
        text=True
    )
    print(gen_html.stdout)
    if gen_html.returncode != 0:
        print(gen_html.stderr, file=sys.stderr)
        sys.exit(gen_html.returncode)
    
    report_path = os.path.abspath(os.path.join('htmlcov', 'index.html'))
    if os.path.exists(report_path):
        print(f"Coverage HTML report generated at:\n{report_path}")
    else:
        print("Coverage report was not generated.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_pytest_with_coverage()
