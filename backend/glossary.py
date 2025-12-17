"""
Defense Glossary Module for Context-Aware Translation
Implements placeholder-based preprocessing for military/defense terminology
ALWAYS-ON for military communication systems
"""
import json
import re
import os
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DefenseGlossary:
    """
    Manages defense terminology glossary and translation preprocessing.
    Uses placeholder protection to preserve military/technical term meanings.
    
    Flow: protect_terms(text) → M2M100 translate → restore_terms(text)
    """
    
    def __init__(self, glossary_path: str = None):
        if glossary_path is None:
            glossary_path = os.path.join(
                os.path.dirname(__file__), 
                "resources", 
                "defense_glossary.json"
            )
        
        self.glossary_path = glossary_path
        self.entries = self._load_glossary()  # List of glossary entries
        self.placeholder_map = {}  # Maps XGLOSSARYX####X -> target translation
        self.source_map = {}       # Maps original matched text -> placeholder
        
    def _load_glossary(self) -> List[Dict[str, Any]]:
        """Load glossary from JSON file and return sorted entries"""
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries = data.get("entries", [])
                
                # Sort by priority (desc) then by term length (desc) for phrase-first matching
                entries.sort(key=lambda e: (
                    -e.get("priority", 0),  # Higher priority first
                    -len(e.get("term", ""))  # Longer terms first
                ))
                
                logger.info(f"✅ Loaded {len(entries)} defense glossary entries")
                return entries
        except FileNotFoundError:
            logger.warning(f"⚠️  Glossary file not found: {self.glossary_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in glossary: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading glossary: {e}")
            return []
    
    def _get_target_field(self, target_lang: str) -> str:
        """Get the target field name for a language (e.g., 'hindi' -> 'target_hi')"""
        lang_codes = {
            "english": "en",
            "hindi": "hi",
            "french": "fr",
            "spanish": "es",
            "german": "de",
            "russian": "ru",
            "chinese": "zh"
        }
        code = lang_codes.get(target_lang.lower(), target_lang[:2])
        return f"target_{code}"
    
    def protect_terms(self, text: str, target_lang: str = "hindi") -> Tuple[str, Dict[str, str]]:
        """
        Protect military/technical terms by replacing with placeholders.
        ALWAYS-ON for defense communication.
        
        Args:
            text: Input text to protect
            target_lang: Target language for translation
            
        Returns:
            Tuple of (protected_text, placeholder_map)
        """
        if not text or not self.entries:
            return text, {}
        
        target_field = self._get_target_field(target_lang)
        
        # Reset maps for this translation
        self.placeholder_map = {}
        self.source_map = {}
        placeholder_counter = 1
        
        protected_text = text
        all_replacements = []  # (start, end, matched_text, target_term, placeholder)
        
        # Entries are already sorted by priority and length (phrase-first)
        for entry in self.entries:
            term = entry.get("term", "")
            target_term = entry.get(target_field)
            
            if not term or not target_term:
                continue
            
            # Build list of all variants to match (term + variants)
            variants_to_match = [term]
            variants = entry.get("variants", [])
            if variants:
                variants_to_match.extend(variants)
            
            for variant in variants_to_match:
                # Word-boundary safe, case-insensitive matching
                pattern = r'\b' + re.escape(variant) + r'\b'
                
                for match in re.finditer(pattern, protected_text, re.IGNORECASE):
                    start_pos = match.start()
                    end_pos = match.end()
                    matched_text = match.group()
                    
                    # Check for overlap with existing replacements (longer terms win)
                    overlap = False
                    for existing_start, existing_end, _, _, _ in all_replacements:
                        if not (end_pos <= existing_start or start_pos >= existing_end):
                            overlap = True
                            break
                    
                    if not overlap:
                        placeholder = f"XGLOSSARYX{placeholder_counter:04d}X"
                        placeholder_counter += 1
                        
                        all_replacements.append((
                            start_pos,
                            end_pos,
                            matched_text,
                            target_term,
                            placeholder
                        ))
        
        # Sort by position (descending) to replace from end to start
        all_replacements.sort(key=lambda x: x[0], reverse=True)
        
        # Apply replacements
        for start_pos, end_pos, matched_text, target_term, placeholder in all_replacements:
            protected_text = (
                protected_text[:start_pos] +
                placeholder +
                protected_text[end_pos:]
            )
            
            self.placeholder_map[placeholder] = target_term
            self.source_map[matched_text] = placeholder
            logger.debug(f"  🔒 '{matched_text}' → {placeholder} → '{target_term}'")
        
        if all_replacements:
            logger.info(f"🔒 Protected {len(all_replacements)} military terms")
        
        return protected_text, self.placeholder_map
    
    def restore_terms(self, text: str, placeholder_map: Dict[str, str]) -> str:
        """
        Restore placeholders with correct target language terms.
        
        Args:
            text: Translated text containing placeholders
            placeholder_map: Map of placeholder -> target term
            
        Returns:
            Final text with military terms restored
        """
        if not placeholder_map or not text:
            return text
        
        restored_text = text
        restoration_count = 0
        
        # Sort placeholders by length (longest first) to avoid partial replacements
        sorted_placeholders = sorted(
            placeholder_map.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for placeholder, target_term in sorted_placeholders:
            # Extract just the number ID from placeholder
            # XGLOSSARYX0001X -> 0001
            match = re.search(r'(\d{4})', placeholder)
            if not match:
                logger.warning(f"⚠️  Invalid placeholder format: {placeholder}")
                continue
            
            placeholder_id = match.group(1)
            
            # Try multiple patterns in order of specificity
            patterns = [
                # Exact match (best case)
                (placeholder, False),
                # Case variations
                (re.compile(re.escape(placeholder), re.IGNORECASE), True),
                # With/without X prefix/suffix: XGLOSSARYX0001X, GLOSSARYX0001X, XGLOSSARYX0001, etc.
                (re.compile(r'X?GLOSSARYX?' + placeholder_id + r'X?', re.IGNORECASE), True),
                # Spaced variations: X GLOSSARY X 0001 X
                (re.compile(r'X?\s*GLOSSARY\s*X?\s*' + placeholder_id + r'\s*X?', re.IGNORECASE), True),
                # Even more flexible: just find GLOSSARY followed by the ID
                (re.compile(r'[_X\s]*GLOSSARY[_X\s]*' + placeholder_id + r'[_X\s]*', re.IGNORECASE), True)
            ]
            
            replaced = False
            for pattern, is_regex in patterns:
                if is_regex:
                    if pattern.search(restored_text):
                        restored_text = pattern.sub(target_term, restored_text)
                        restoration_count += 1
                        logger.debug(f"  ✅ {placeholder} → '{target_term}'")
                        replaced = True
                        break
                else:
                    if pattern in restored_text:
                        restored_text = restored_text.replace(pattern, target_term)
                        restoration_count += 1
                        logger.debug(f"  ✅ {placeholder} → '{target_term}'")
                        replaced = True
                        break
            
            if not replaced:
                logger.warning(f"⚠️  Could not restore placeholder: {placeholder} in text")
        
        if restoration_count:
            logger.info(f"✅ Restored {restoration_count} military terms")
        
        return restored_text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the glossary"""
        if not self.entries:
            return {"total_entries": 0}
        
        # Count by tags
        tag_counts = {}
        priority_distribution = {}
        multi_word_count = 0
        
        for entry in self.entries:
            # Count tags
            tags = entry.get("tags", [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Count priorities
            priority = entry.get("priority", 0)
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            
            # Count multi-word phrases
            term = entry.get("term", "")
            if " " in term:
                multi_word_count += 1
        
        return {
            "total_entries": len(self.entries),
            "multi_word_phrases": multi_word_count,
            "tag_counts": tag_counts,
            "priority_distribution": priority_distribution,
            "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }


# Singleton instance
_glossary_instance = None


def get_glossary() -> DefenseGlossary:
    """Get or create global glossary instance (singleton pattern)"""
    global _glossary_instance
    if _glossary_instance is None:
        _glossary_instance = DefenseGlossary()
        logger.info("🔧 Defense glossary initialized (ALWAYS-ON mode)")
    return _glossary_instance
