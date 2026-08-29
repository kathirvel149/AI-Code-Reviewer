import streamlit as st
import subprocess
import black
import re
import ast
from radon.complexity import cc_visit

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)
st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)
with st.sidebar:
    st.header("🤖 AI Code Reviewer")

    st.write("Automated Python Code Analysis")

    st.divider()

    st.subheader("🔍 Analysis Tools")

    st.write("✅ Flake8")
    st.write("✅ Black Formatter")
    st.write("✅ Radon Complexity")
    st.write("✅ Security Scanner")
    st.write("✅ Code Metrics")
    st.write("✅ Smart Suggestions")

    st.divider()

    st.caption("💡 Upload a Python file to begin.")

st.markdown(
    '<div class="main-title">🤖 AI Code Reviewer</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    ### Analyze • Review • Improve

    Upload your Python file and get an automated code quality report
    using **Flake8, Black, Radon, and Security Checks**.
    """
)

st.info(
    "📌 Upload a Python (.py) file below to start the code review."
)

st.caption("🔒 Your uploaded code is analyzed locally by the application.")

uploaded_file = st.file_uploader(
    "Upload your Python file",
    type=["py"]
)

if uploaded_file is None:
    st.stop()

code = uploaded_file.read().decode("utf-8")
st.caption(f"📄 File: {uploaded_file.name}")
st.subheader("Uploaded Code")
st.code(code, language="python")
st.divider()

result = subprocess.run(
    ["flake8", "--stdin-display-name=uploaded.py", "--ignore=E303,W391,W292", "-"],
    input=code,
    text=True,
    capture_output=True
)

st.subheader("Flake8 Analysis")

if result.stdout:
    st.code(result.stdout)
else:
    st.success("No Flake8 issues found!")
st.divider()
try:
   formatted_code = black.format_str(code, mode=black.Mode())

   st.subheader("Black Formatting")

   st.code(formatted_code, language="python")

except Exception as e:
     st.error(f"Black could not format the code: {e}")

st.subheader("Radon Complexity")

try:
    complexity_results = cc_visit(code)

    if complexity_results:
        for item in complexity_results:
            st.write(f"**{item.name}**")
            st.write(f"Complexity: {item.complexity}")
    else:
        st.info("No functions or classes found to analyze.")

except Exception as e:
        st.error(f"Radon could not analyze the code: {e}")     

if result.stdout:
        issue_count = len(result.stdout.strip().splitlines())
else:
        issue_count = 0

score = max(0, 100 - (issue_count * 5))

st.subheader("🏆 Overall Code Quality")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏆 Code Quality Score",
        f"{score}/100"
    )
    st.progress(score / 100)

with col2:
    st.metric(
        "🔍 Flake8 Issues",
        issue_count
    )

with col3:
    if complexity_results:
        current_complexity = max(
            item.complexity for item in complexity_results
        )
    else:
        current_complexity = 0

    st.metric(
        "🧠 Complexity",
        current_complexity
    )

if score >= 80:
    st.success("✅ Good Code Quality")
elif score >= 60:
    st.warning("⚠️ Code Quality Needs Improvement")
else:
    st.error("❌ Poor Code Quality")

if score >= 80:
    quality_status = "Good"
elif score >= 60:
    quality_status = "Needs Improvement"
else:
    quality_status = "Poor"
if complexity_results:
    max_complexity = max(
        item.complexity for item in complexity_results
    )
else:
    max_complexity = 0    
    
st.subheader("📊 Code Review Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.write("**Code Quality**")
    st.write(f"🏆 {quality_status}")

with col2:
    st.write("**Flake8 Issues**")
    st.write(f"🔍 {issue_count}")

with col3:
    st.write("**Black Formatting**")
    st.write("✅ Completed")

with col4:
    st.write("**Highest Complexity**")
    st.write(f"🧠 {max_complexity}")

if issue_count == 0 and max_complexity <= 5:
    st.success(
        "🎉 Excellent! Your code has good style and low complexity."
    )
elif issue_count > 0 and max_complexity <= 5:
    st.warning(
        "⚠️ Fix the Flake8 issues to improve your code quality."
    )
else:
    st.warning(
        "⚠️ Consider simplifying complex parts of your code."
    )

st.subheader("📥 Download Formatted Code")

st.download_button(
    label="Download Formatted Python File",
    data=formatted_code,
    file_name="formatted_code.py",
    mime="text/x-python"
)
st.subheader("🔐 Security Vulnerability Scan")

security_issues = []

if re.search(
    r'(?i)(password|passwd|pwd)\s*=\s*[\'"].*[\'"]',
    code
):
    security_issues.append(
        "Hardcoded password detected. Avoid storing passwords directly in source code."
    )

if re.search(r'\beval\s*\(', code):
    security_issues.append(
        "Use of eval() detected. Avoid eval() with untrusted input."
    )

if re.search(r'\bexec\s*\(', code):
    security_issues.append(
        "Use of exec() detected. It can execute arbitrary Python code."
    )

if re.search(
    r'subprocess\..*shell\s*=\s*True',
    code
):
    security_issues.append(
        "subprocess with shell=True detected. This can create command injection risks."
    )

if re.search(
    r'(?i)(select|insert|update|delete).*["\']\s*\+',
    code
):
    security_issues.append(
        "Possible SQL query string concatenation detected. Use parameterized queries."
    )

if security_issues:
    st.error(
        f"🚨 {len(security_issues)} Security Issue(s) Detected"
    )

    for issue in security_issues:
        st.warning(f"⚠️ {issue}")

else:
    st.success(
        "🛡️ No basic security vulnerabilities detected."
    )
st.subheader("🛡️ Advanced Security Checks")

sql_injection = False
command_injection = False

if re.search(
    r"execute\s*\(.*%|execute\s*\(.*\+|SELECT.*\+",
    code,
    re.IGNORECASE
):
    sql_injection = True

if re.search(
    r"os\.system\s*\(|subprocess\.call\s*\(.*shell\s*=\s*True|subprocess\.Popen\s*\(.*shell\s*=\s*True",
    code
):
    command_injection = True
security_total = len(security_issues)

if sql_injection:
    security_total += 1

if command_injection:
    security_total += 1    

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.write("**🔐 Security Risk**")

    if security_issues or sql_injection or command_injection:
        st.error("🚨 Risk Detected")
    else:
        st.success("🟢 Low Risk")

with col2:
    st.write("**💉 SQL Injection**")

    if sql_injection:
        st.error("🚨 Detected")
    else:
        st.success("✅ Safe")

with col3:
    st.write("**💻 Command Injection**")

    if command_injection:
        st.error("🚨 Detected")
    else:
        st.success("✅ Safe")

with col4:
    st.write("**🔎 Security Issues**")
    st.metric(
        "Detected",
        security_total
    )        
st.subheader("📊 Code Metrics")

try:
    tree = ast.parse(code)

    total_lines = len(code.splitlines())

    function_count = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for node in ast.walk(tree)
    )

    class_count = sum(
        isinstance(node, ast.ClassDef)
        for node in ast.walk(tree)
    )

    comment_count = sum(
        1 for line in code.splitlines()
        if line.strip().startswith("#")
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📄 Total Lines", total_lines)

    with col2:
        st.metric("⚙️ Functions", function_count)

    with col3:
        st.metric("🏛️ Classes", class_count)

    with col4:
        st.metric("💬 Comments", comment_count)

except Exception as e:
    st.error(f"Could not calculate code metrics: {e}") 

st.subheader("❤️ Code Health")

if score >= 80 and max_complexity <= 5 and len(security_issues) == 0:
    st.success("🟢 Excellent Code Health")
elif score >= 60 and max_complexity <= 10:
    st.warning("🟡 Moderate Code Health")
else:
    st.error("🔴 Code Health Needs Improvement")

st.subheader("🤖 Smart Code Suggestions")

suggestions = []

if issue_count > 0:
    suggestions.append(
        f"⚠️ Fix the {issue_count} Flake8 issue(s) "
        "to improve code style and readability."
    )
else:
    suggestions.append(
        "✅ No Flake8 issues found. "
        "Your code follows good basic style."
    )

if complexity_results:
    if max_complexity <= 5:
        suggestions.append(
            f"🧠 Complexity is {max_complexity}. "
            "The code structure is relatively simple."
        )
    elif max_complexity <= 10:
        suggestions.append(
            f"🧠 Complexity is {max_complexity}. "
            "Consider simplifying some conditions."
        )
    else:
        suggestions.append(
            f"🚨 Complexity is {max_complexity}. "
            "Consider breaking complex functions into smaller functions."
        )

if security_issues:
    suggestions.append(
        f"🔐 {len(security_issues)} security issue(s) detected. "
        "Review the security warnings before using the code."
    )
else:
    suggestions.append(
        "✅ No basic security issues detected."
    )

suggestions.append(
    "💡 Use meaningful variable and function names."
)

suggestions.append(
    "💡 Keep functions small and focused on one task."
)

for suggestion in suggestions:
    st.info(suggestion)

st.subheader("📄 Download Code Review Report")

report = f"""
==================================================
              AI CODE REVIEWER REPORT
==================================================

📊 OVERALL RESULTS
------------------
Code Quality Score : {score}/100
Flake8 Issues      : {issue_count}
Highest Complexity : {max_complexity}
Black Formatting   : Completed
Security Issues    : {len(security_issues)}

📈 CODE METRICS
---------------
Total Lines        : {total_lines}
Functions          : {function_count}
Classes            : {class_count}
Comments           : {comment_count}

🔐 SECURITY STATUS
------------------
Basic Security Issues : {len(security_issues)}
SQL Injection         : {"Detected" if sql_injection else "Not Detected"}
Command Injection     : {"Detected" if command_injection else "Not Detected"}

📝 REVIEW SUMMARY
-----------------
Code Quality : {quality_status}

"""

if issue_count == 0:
    report += "Flake8 : No issues found.\n"
else:
    report += f"Flake8 : {issue_count} issue(s) found.\n"

if max_complexity <= 5:
    report += "Complexity : Acceptable.\n"
else:
    report += "Complexity : Consider simplifying the code.\n"

if security_issues:
    report += f"Security : {len(security_issues)} issue(s) detected.\n"
else:
    report += "Security : No basic security issues detected.\n"

report += """
💡 SMART SUGGESTIONS
--------------------
"""

for suggestion in suggestions:
    report += f"- {suggestion}\n"

report += """
==================================================
             END OF REVIEW REPORT
==================================================
"""

st.download_button(
    label="📥 Download Full Review Report",
    data=report,
    file_name="AI_Code_Review_Report.txt",
    mime="text/plain"
)