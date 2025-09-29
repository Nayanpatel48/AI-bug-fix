import gradio as gr, os, tempfile, shutil, time, subprocess, difflib
from ai_client import call_ai

# Note: The functions from the old 'utils.py' are now defined locally below

ROOT = os.getcwd()
FILES = sorted(os.listdir("seeded_repo"))


# --- Local Utility Functions (The key change is here) ---

def run_pytests(path=".", test_target=".", timeout=30):
    """Runs pytest in a given directory, targeting a specific file or the whole suite."""
    t0 = time.perf_counter()
    
    # Run pytest, targeting the specific test file path
    # test_target will be 'tests/test_mod1.py' or similar
    cmd = ["pytest", "-q", "--disable-warnings", test_target]
    
    p = subprocess.run(cmd, cwd=path,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, text=True)
    dt = time.perf_counter() - t0
    out = p.stdout
    passed = "passed" in out and "failed" not in out
    return {"passed": passed, "output": out, "time": dt, "returncode": p.returncode}

def compute_diff(old, new, fname="file"):
    """Computes a unified diff."""
    a = old.splitlines(keepends=True)
    b = new.splitlines(keepends=True)
    return "".join(difflib.unified_diff(a, b, fromfile=fname, tofile=fname, lineterm=""))

def copy_repo(src="seeded_repo", dst=None):
    """Creates a temporary, isolated working copy."""
    if dst is None:
        dst = tempfile.mkdtemp(prefix="work_")
    
    # Copy project files
    shutil.copytree(src, os.path.join(dst, "seeded_repo"), dirs_exist_ok=True)
    shutil.copytree("tests", os.path.join(dst, "tests"), dirs_exist_ok=True)
    
    # Copy pytest config (THE FIX)
    shutil.copyfile("pytest.ini", os.path.join(dst, "pytest.ini")) 
    
    return dst


# --- Gradio UI Logic ---

def load_file(fname):
    return open(os.path.join("seeded_repo", fname)).read()

def run_tests_for(fname):
    work = copy_repo()
    
    # Determine the specific test file to run
    test_target = os.path.join("tests", f"test_{fname.replace('.py','')}.py")
    
    res = run_pytests(work, test_target) # Run ONLY the targeted test
    shutil.rmtree(work, ignore_errors=True)
    
    # Highlight status for video
    status = "✅ TEST PASSED (Unexpected - Check the File!)" if res["passed"] else "❌ TEST FAILED (Bug Confirmed)"
    return status + "\n\n" + res["output"]

def ask_ai(fname, content):
    t0=time.perf_counter()
    out = call_ai(fname, content)
    
    # The status box in the UI will now show the generation time
    return out, f"AI generation time: {round(time.perf_counter()-t0, 3)}s"

def apply_patch_and_test(fname, new_content):
    work = copy_repo()
    target = os.path.join(work, "seeded_repo", fname)
    old = open(target, "r").read()
    
    # Overwrite file with AI suggestion
    open(target, "w").write(new_content)
    
    # Determine the specific test file to run
    test_target = os.path.join("tests", f"test_{fname.replace('.py','')}.py")
    
    res = run_pytests(work, test_target) # Run ONLY the targeted test
    diff = compute_diff(old, new_content, fname)
    shutil.rmtree(work, ignore_errors=True)
    
    # Highlight status for video
    status = "✅ SUCCESS! TEST PASSED" if res["passed"] else "❌ FAILURE! TEST STILL FAILS"
    
    return status + "\n\n" + res["output"], diff


# --- Gradio Interface (Unchanged) ---

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Fix Benchmark — Live Gradio Demo")
    
    with gr.Row():
        fname = gr.Dropdown(choices=FILES, value=FILES[0], label="1. Select File to Test", scale=1)
        load_btn = gr.Button("Load File Content", scale=0, variant="secondary")
    
    code = gr.Textbox(lines=8, label="File Content (The Bug)", interactive=False)
    
    with gr.Row():
        run_btn = gr.Button("2. Run Pytests (Confirm Failure)", variant="stop", scale=1)
        ai_btn = gr.Button("3. Ask Gemini to Patch (Model Call)", variant="primary", scale=1)
        apply_btn = gr.Button("4. Apply Patch & Rerun Tests", variant="success", scale=1)
    
    test_output = gr.Textbox(lines=6, label="Pytest Output (Initial Run & AI Generation Time)", interactive=False)
    
    with gr.Row():
        ai_output = gr.Textbox(lines=8, label="AI Suggested File Content", interactive=False, scale=1)
        diff_box = gr.Textbox(lines=8, label="Unified Diff (Original vs. AI Fix)", interactive=False, scale=1)

    post_output = gr.Textbox(lines=6, label="Post-Apply Pytest Output (Final Result)", interactive=False)

    
    # --- Event Handlers ---
    load_btn.click(lambda f: load_file(f), inputs=fname, outputs=code)
    run_btn.click(lambda f: run_tests_for(f), inputs=fname, outputs=test_output)
    ai_btn.click(lambda f,c: ask_ai(f,c), inputs=[fname,code], outputs=[ai_output, test_output])
    apply_btn.click(lambda f,nc: apply_patch_and_test(f,nc), inputs=[fname,ai_output], outputs=[post_output,diff_box])

demo.launch(server_name="0.0.0.0", share=False)