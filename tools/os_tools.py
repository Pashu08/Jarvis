import os
import subprocess
import difflib
import time

class ShizukuExecutor:
    """Core execution layer utilizing Shizuku (rish) for elevated shell access."""
    
    @staticmethod
    def run(command):
        print(f"[DEBUG] ShizukuExecutor Executing: {command}")
        try:
            rish_path = os.path.expanduser("~/storage/downloads/Shizuku/rish")
            # Added timeout=15 to prevent hanging shell commands
            result = subprocess.run(
                ["sh", rish_path, "-c", command],
                capture_output=True,
                text=True,
                check=True,
                timeout=15
            )
            return ( (result.stdout or "") + (result.stderr or "") ).strip()
            
        except subprocess.TimeoutExpired:
            print("[Shizuku Execution Error]: Command timed out after 15 seconds.")
            return "Error: Command execution timed out."
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown OS error."
            print(f"[Shizuku Execution Error]: {error_msg}")
            return ( (e.stdout or "") + (e.stderr or "") ).strip()
        except Exception as e:
            print(f"[System Error]: Shizuku execution failed: {e}")
            return "Error: Shizuku execution failed."

class PackageDiscovery:
    """Service to discover and cache installed Android packages."""
    
    _cached_packages = []
    _last_refresh_time = 0

    @classmethod
    def get_packages(cls, force_refresh=False):
        current_time = time.time()
        if not cls._cached_packages or force_refresh or (current_time - cls._last_refresh_time > 300):
            print("[DEBUG] PackageDiscovery: Querying Android for installed packages...")
            stdout = ShizukuExecutor.run("cmd package list packages")
                
            if stdout and "package:" in stdout:
                pkgs = []
                for line in stdout.splitlines():
                    clean_line = line.strip()
                    if clean_line.startswith("package:"):
                        pkgs.append(clean_line.replace("package:", ""))
                        
                # SAFEGUARD: Never overwrite a good cache with an empty one on failure
                if pkgs:
                    cls._cached_packages = pkgs
                    cls._last_refresh_time = current_time
                    print(f"[DEBUG] PackageDiscovery: Parsed {len(cls._cached_packages)} packages.")
                else:
                    print("[DEBUG] PackageDiscovery: Warning - No packages parsed. Retaining old cache.")
            else:
                print("[DEBUG] PackageDiscovery: Warning - Query failed or empty. Retaining old cache.")
        else:
            print("[DEBUG] PackageDiscovery: Using cached package list.")
            
        return cls._cached_packages

class ActivityResolver:
    """Service to dynamically resolve and cache the main launch activity of a package."""
    
    _cached_activities = {}
    
    @classmethod
    def resolve(cls, package_name):
        if package_name in cls._cached_activities:
            print(f"[DEBUG] ActivityResolver: Using cached activity for {package_name}")
            return cls._cached_activities[package_name]
            
        print(f"[DEBUG] ActivityResolver: Resolving activity for {package_name}...")
        stdout = ShizukuExecutor.run(f"cmd package resolve-activity --brief {package_name}")
        if stdout and "Error" not in stdout:
            lines = stdout.splitlines()
            for line in reversed(lines):
                if "/" in line:
                    component = line.strip()
                    cls._cached_activities[package_name] = component
                    print(f"[DEBUG] ActivityResolver: Successfully resolved to {component}")
                    return component
                    
        print(f"[DEBUG] ActivityResolver: Failed to resolve activity for {package_name}.")
        return None

class FuzzyMatcher:
    """Service to handle misspellings, plurals, and map plain English to package names."""
    
    @staticmethod
    def match(target_app, packages):
        target_clean = target_app.replace(" ", "").lower()
        
        variation_map = {
            "setting": "settings",
            "settingss": "settings",
            "chrom": "chrome",
            "chorme": "chrome",
            "whatsap": "whatsapp",
            "whatsapp": "whatsapp",
            "insta": "instagram",
            "ig": "instagram",
            "snap": "snapchat",
            "spot": "spotify"
        }
        target_clean = variation_map.get(target_clean, target_clean)
        print(f"[DEBUG] FuzzyMatcher: Cleaned target intent -> '{target_clean}'")
        
        substring_matches = [pkg for pkg in packages if target_clean in pkg.lower()]
        if substring_matches:
            matched = min(substring_matches, key=len)
            print(f"[DEBUG] FuzzyMatcher: Substring match found -> {matched}")
            return matched
            
        package_map = {}
        for pkg in packages:
            parts = pkg.split('.')
            if len(parts) > 1:
                meaningful_name = parts[-1] if parts[-1] != "android" else parts[-2]
            else:
                meaningful_name = pkg
            
            package_map[meaningful_name.lower()] = pkg
            
        matches = difflib.get_close_matches(target_clean, package_map.keys(), n=1, cutoff=0.6)
        if matches:
            matched = package_map[matches[0]]
            print(f"[DEBUG] FuzzyMatcher: Difflib match found -> {matched}")
            return matched
            
        print("[DEBUG] FuzzyMatcher: No match found.")
        return None

def launch_package(package_name):
    """Dual-strategy execution layer to safely launch Android packages."""
    # STEP 1: Attempt native Activity resolution and launch
    component = ActivityResolver.resolve(package_name)
    if component:
        print("[DEBUG] Launch Method: Activity")
        launch_result = ShizukuExecutor.run(f"am start -n {component}")
        
        # Verify launch succeeded by ensuring NO Android-level error outputs exist
        if launch_result is not None:
            lower_res = launch_result.lower()
            failure_keywords = ["error", "exception", "does not exist", "unable", "activity not found", "securityexception"]
            if not any(err in lower_res for err in failure_keywords):
                return True

    # STEP 2: Fallback to Monkey injection launcher
    print("[DEBUG] Launch Method: Monkey")
    monkey_cmd = f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
    monkey_output = ShizukuExecutor.run(monkey_cmd)
    
    if monkey_output and "Events injected: 1" in monkey_output:
        return True
        
    return False

def send_keyevent(keycode):
    """Reusable helper function to inject Android keyevents via Shizuku."""
    return ShizukuExecutor.run(f"input keyevent {keycode}")

def get_current_app_name():
    """Detects foreground app via dumpsys prioritizing mCurrentFocus then mFocusedApp."""
    try:
        out = ShizukuExecutor.run("dumpsys window | grep mCurrentFocus")
        
        # Robust handling for null/empty focus windows
        if not out or "mcurrentfocus=null" in out.lower() or "error" in out.lower():
            out = ShizukuExecutor.run("dumpsys window | grep mFocusedApp")
            
        if out and "error" not in out.lower():
            parts = out.split()
            for p in parts:
                if "/" in p and ("com." in p or "net." in p or "org." in p or "io." in p or "app." in p):
                    pkg = p.split("/")[0].replace("}", "").strip()
                    return pkg if pkg else "Unknown App"
    except Exception as e:
        print(f"[DEBUG] Failed to parse current app: {e}")
    return "Unknown App"

def tool_health_check():
    """Validates structural readiness of the OS automation components."""
    errors = []
    
    rish_path = os.path.expanduser("~/storage/downloads/Shizuku/rish")
    if not os.path.exists(rish_path):
        errors.append(f"Shizuku 'rish' binary path missing at {rish_path}")
        
    try:
        pkgs = PackageDiscovery.get_packages(force_refresh=False)
        if not pkgs:
            errors.append("PackageDiscovery cache returned an empty list or execution failed.")
    except Exception as e:
        errors.append(f"PackageDiscovery failure: {str(e)}")
        
    if errors:
        return "Critical Component Error:\n" + "\n".join(f"- {err}" for err in errors)
    return "Healthy"

def execute_tool(intent, payload=None):
    """Central execution engine for the OS Tool Subsystem."""
    print(f"\n[DEBUG] execute_tool triggered | Intent: {intent} | Payload: {payload}")
    
    try:
        # --- NAVIGATION SYSTEM ---
        if intent == "home":
            res = send_keyevent(3)
            if res is None or "error" in res.lower() or "exception" in res.lower():
                return "Execution Error: Failed to go Home."
            return "Successfully went Home."
            
        elif intent == "back":
            res = send_keyevent(4)
            if res is None or "error" in res.lower() or "exception" in res.lower():
                return "Execution Error: Failed to press Back."
            return "Successfully pressed Back."
            
        elif intent == "recent_apps":
            res = send_keyevent(187)
            if res is None or "error" in res.lower() or "exception" in res.lower():
                return "Execution Error: Failed to open Recent Apps."
            return "Successfully opened Recent Apps."

        # --- SYSTEM STATE SYSTEM ---
        elif intent == "current_app":
            pkg = get_current_app_name()
            return f"Successfully retrieved current app: {pkg}"

        # --- INPUT INJECTION SYSTEM ---
        elif intent == "type_text":
            if not payload: 
                return "Error: No text provided to type."
            escaped_text = payload.replace(" ", "%s")
            res = ShizukuExecutor.run(f"input text {escaped_text}")
            if res is None or "error" in res.lower() or "killed" in res.lower() or "exception" in res.lower():
                return "Execution Error: Failed to type text."
            return f"Successfully typed: {payload}"

        elif intent == "tap":
            if not payload: 
                return "Error: No coordinates provided for tap."
            coords = payload.strip().split()
            if len(coords) != 2 or not all(c.isdigit() for c in coords):
                return "Error: Invalid tap coordinates. Must be 'X Y' integers."
                
            res = ShizukuExecutor.run(f"input tap {payload}")
            if res is None or "error" in res.lower() or "exception" in res.lower():
                return f"Execution Error: Failed to tap at {payload}."
            return f"Successfully tapped {payload}."

        elif intent == "swipe":
            if not payload:
                return "Error: No direction provided for swipe."
            direction = payload.strip().lower()
            coords = ""
            if direction == "up": coords = "500 1500 500 500"
            elif direction == "down": coords = "500 500 500 1500"
            elif direction == "left": coords = "800 1000 200 1000"
            elif direction == "right": coords = "200 1000 800 1000"
            else: return f"Error: Invalid swipe direction '{direction}'."
            
            res = ShizukuExecutor.run(f"input swipe {coords}")
            if res is None or "error" in res.lower() or "exception" in res.lower():
                return f"Execution Error: Failed to swipe {direction}."
            return f"Successfully swiped {direction}."

        # --- APP MANAGEMENT SYSTEM ---
        elif intent == "close_app":
            if not payload: 
                return "Error: No app specified to close."
            target_app = payload.strip().lower()
            packages = PackageDiscovery.get_packages(force_refresh=False)
            matched_package = FuzzyMatcher.match(target_app, packages)
            
            if not matched_package:
                packages = PackageDiscovery.get_packages(force_refresh=True)
                matched_package = FuzzyMatcher.match(target_app, packages)
                
            if matched_package:
                res = ShizukuExecutor.run(f"am force-stop {matched_package}")
                if res and ("error" in res.lower() or "exception" in res.lower()):
                    return f"Execution Error: Failed to close {target_app.title()}."
                return f"Successfully closed {target_app.title()}."
            return f"Error: Application '{target_app}' could not be found to close."

        elif intent == "open_app" or intent.startswith("open_"):
            if intent == "open_app":
                if not payload: 
                    return "Error: Cannot open application without a target payload."
                target_app = payload.strip().lower()
            else:
                target_app = intent.replace("open_", "").strip().lower()

            packages = PackageDiscovery.get_packages(force_refresh=False)
            matched_package = FuzzyMatcher.match(target_app, packages)
            
            if not matched_package:
                print("[DEBUG] App not found in cache. Refreshing package list...")
                packages = PackageDiscovery.get_packages(force_refresh=True)
                matched_package = FuzzyMatcher.match(target_app, packages)
            
            if matched_package:
                success = launch_package(matched_package)
                if success:
                    return f"Successfully opened {target_app.title()}."
                else:
                    return f"Execution Error: Failed to launch {target_app.title()}."
            return f"Error: Application '{target_app}' could not be resolved or found."

        return f"Error: Tool intent '{intent}' is unsupported by the OS layer."

    except Exception as e:
        print(f"[DEBUG] Fatal Execution Error: {str(e)}")
        return f"Execution Error: Failed to process command due to: {str(e)}"

# --- INITIALIZATION ---
print("[DEBUG] Initializing OS Tools and preloading Android packages...")
PackageDiscovery.get_packages(force_refresh=True)
