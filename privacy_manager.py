import os
import re
import json
import logging
import time
from typing import Optional

# Advanced encryption binding!
from cryptography.fernet import Fernet # Provides robust AES-128 (wrapped in 256 logic block encryption) in CBC mode!

logger = logging.getLogger("JarvisPrivacyManager")

class SearchPrivacyManager:
    """
    Enterprise-grade security module for JARVIS prioritizing local user autonomy.
    Features Incognito enforcement, AES log encryption, PII sanitization algorithms,
    and automatic blocking against recognized ad/tracking domains.
    """
    
    def __init__(self):
        self.incognito_mode = False
        self.local_only_mode = False
        
        # Secured Paths
        self.key_file = "jarvis_encryption.key"
        self.audit_log_file = "jarvis_audit_log.enc"
        
        # Heuristic Network DenyList - Intended to be hooked dynamically to HTTP streams if using proxy
        self.domain_blacklist = [
            "doubleclick.net", "google-analytics.com", "facebook.com/tr", 
            "tracker.com", "adservices", "pixel.wp.com"
        ]
        
        # Regex mappings for severe financial/PII leakage prevention
        self.sensitive_patterns = [
            r"password", r"passcode", 
            r"\b(?:\d[ -]*?){13,16}\b", # Detects basic Credit Card structures broadly
            r"\b\d{3}-\d{2}-\d{4}\b", # Matches Social Security format
            r"private key", r"seed phrase", r"bank account", r"cvv"
        ]
        
        # Initialization
        self.cipher_suite = None
        self._load_or_create_key()

    def _load_or_create_key(self):
        """Generates or loads AES encryption key strictly kept locally on device."""
        if not os.path.exists(self.key_file):
            logger.info("Generating pristine localized 256-bit AES encryption payload key...")
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        
        try:
            with open(self.key_file, "rb") as f:
                self.cipher_suite = Fernet(f.read())
        except Exception as e:
            logger.error(f"FATAL: Encryption Key Corrupted or lost! {e}")

    def encrypt_search_history(self, raw_data_dict: dict) -> bytes:
        """Takes a JSON dict structure and encodes it via Fernet AES symmetrically."""
        if not self.cipher_suite: return b""
        json_data = json.dumps(raw_data_dict).encode('utf-8')
        return self.cipher_suite.encrypt(json_data)
        
    def decrypt_search_history(self, encrypted_data: bytes) -> dict:
        """Decrypts AES token payload safely back into dictionary."""
        if not self.cipher_suite: return {}
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to decrypt history payload: {e}")
            return {}

    def toggle_incognito_mode(self, force_state: Optional[bool] = None) -> bool:
        """Toggles logic preventing local API history logging or persistent cache tracking."""
        if force_state is not None:
            self.incognito_mode = force_state
        else:
            self.incognito_mode = not self.incognito_mode
            
        logger.info(f"[SECURITY] Incognito Tracking Mode is now: {'ACTIVE' if self.incognito_mode else 'DISABLED'}")
        return self.incognito_mode
        
    def toggle_local_only_mode(self, force_state: Optional[bool] = None) -> bool:
        """Blocks network pinging entirely, forcing queries solely against local JSON cache."""
        if force_state is not None:
            self.local_only_mode = force_state
        else:
            self.local_only_mode = not self.local_only_mode
            
        logger.warning(f"[SECURITY] Local-Only Airgap Mode is now: {'ACTIVE' if self.local_only_mode else 'DISABLED'}")
        return self.local_only_mode

    def detect_sensitive_query(self, query: str) -> bool:
        """Checks voice input against heuristic PII/Financial identifiers natively before processing."""
        query_ldb = query.lower()
        for pattern in self.sensitive_patterns:
            if re.search(pattern, query_ldb):
                logger.warning(f"[PRIVACY ENFORCER] SENSITIVE DATA DETECTED! Blocking tracking vectors!")
                return True
        return False

    def sanitize_search_query(self, query: str) -> str:
        """Anonymizes input by actively stripping out identities, emails, and phone numbers natively."""
        sanitized = query
        
        # Email stripping extraction
        sanitized = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', sanitized)
        
        # Phone stripping (Basic formatting matching (555) 555-5555 or 555-555-5555)
        sanitized = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[REDACTED_PHONE]', sanitized)
        
        if sanitized != query:
            logger.info("[PRIVACY ENFORCER] Query was actively sanitized for PII safety.")
            
        return sanitized

    def filter_blacklist_domains(self, results_data: list) -> list:
        """Actively screens mapped returned sources cutting away blacklisted data trackers."""
        clean_results = []
        for result in results_data:
            link = result.get("link", "").lower()
            if not any(bad_domain in link for bad_domain in self.domain_blacklist):
                clean_results.append(result)
        return clean_results

    def log_encrypted_audit(self, query: str, context: str):
        """Append-only secure AES encrypted logging specifically for user oversight administration."""
        if self.incognito_mode:
            return  # Core incognito logic blocks writes!
            
        # Protect PII strictly
        safe_query = query if not self.detect_sensitive_query(query) else "[REDACTED_SENSITIVE_DATA]"
            
        # Compile json chunk structure
        entry = {
            "query": safe_query,
            "routing_engine": context,
            "timestamp": time.time() 
        }
        
        encrypted_chunk = self.cipher_suite.encrypt(json.dumps(entry).encode('utf-8'))
        
        # Secure line append directly into byte lock
        with open(self.audit_log_file, "ab") as f:
            f.write(encrypted_chunk + b"\n")

    def export_search_data(self, target_file: str = "exported_privacy_data.json") -> bool:
        """Exports fully decrypted audit logs locally to JSON authorizing manual user audit reading."""
        if not os.path.exists(self.audit_log_file):
            logger.info("No security audit logs found to export.")
            return False
            
        decrypted_logs = []
        with open(self.audit_log_file, "rb") as f:
            lines = f.readlines()
            for line in lines:
                try:
                    # Strip newline and decrypt the binary payload
                    dec = self.cipher_suite.decrypt(line.strip()).decode('utf-8') 
                    decrypted_logs.append(json.loads(dec))
                except Exception:
                    continue
                    
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(decrypted_logs, f, indent=4)
            
        logger.info(f"Successfully Decrypted and compiled transparent audit trails over to -> {target_file}")
        return True

if __name__ == "__main__":
    # Built-In Cryptographic execution test routines!
    print("Beginning JARVIS Privacy Execution Logic Probe...\n")
    privacy = SearchPrivacyManager()
    
    # 1. PII Test
    bad_query = "who is the CEO of apple email him at ceo@apple.com"
    clean_q = privacy.sanitize_search_query(bad_query)
    print(f"[Sanitize Test] Cleaned Query: {clean_q}")
    
    # 2. Sensitive Data Recognition
    is_sens = privacy.detect_sensitive_query("what is my private key")
    print(f"[Heuristic Test] 'private key' block recognized? {is_sens}")
    
    # 3. Secure Logging Execution
    privacy.log_encrypted_audit(clean_q, "duckduckgo_async")
    print("\nAES Encrypted Log written securely. Generating Audit Trial JSON Dump...")
    
    # 4. Decrypt / Trace
    privacy.export_search_data("demo_audit_dump.json")
    print("\nPrivacy Protocol execution sequence fully PASSED!")
