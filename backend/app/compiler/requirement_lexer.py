import re
from typing import Optional

from app.schemas.ast_models import Token, TokenType

# Keyword dictionaries
ENTITY_KEYWORDS = {"user", "contact", "product", "order", "customer", "account", "team", "project", "task", "patient", "appointment", "prescription", "doctor", "record", "course", "lesson", "quiz", "enrollment", "certificate", "instructor", "listing", "agent", "tour", "mortgage", "search", "menu", "reservation", "table", "kitchen", "delivery", "posting", "application", "company", "resume", "interview", "subscription", "invoice", "usage", "payment", "revenue"}
ACTION_KEYWORDS = {"login", "logout", "create", "read", "update", "delete", "view", "search", "filter", "export", "import", "approve", "reject", "assign", "notify", "checkout", "tracking", "parsing", "scheduling", "metering"}
FEATURE_KEYWORDS = {"dashboard", "analytics", "notifications", "settings", "profile", "inbox", "calendar", "chat", "cart", "panel", "board", "moderation", "calculator", "display"}
ROLE_KEYWORDS = {"admin", "user", "manager", "editor", "viewer", "moderator", "owner", "superadmin", "instructor", "agent"}
CONSTRAINT_KEYWORDS = {"role-based", "premium", "required", "unique", "encrypted", "private", "public", "secure"}
PLAN_KEYWORDS = {"free", "basic", "premium", "enterprise", "pro", "starter", "business"}
INTEGRATION_KEYWORDS = {"payment", "stripe", "analytics", "email", "sms", "notification", "webhook"}
RELATION_KEYWORDS = {"with", "has", "belongs", "contains", "manages", "owns"}
MODIFIER_KEYWORDS = {"real-time", "automated", "custom", "advanced", "basic", "simple"}


class RequirementLexer:
    """
    Hybrid tokenizer: Regex + Dictionary matching.
    Optionally enriches with spaCy if available.
    """

    def __init__(self):
        try:
            from app.config import get_settings
            import spacy
            settings = get_settings()
            self.nlp = spacy.load(settings.spacy_model)
            self.use_spacy = True
        except (ImportError, Exception):
            self.nlp = None
            self.use_spacy = False

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        
        # Simple regex tokenizer
        pattern = re.compile(r'([\w\-]+|[^\w\s])')
        
        lines = text.split('\n')
        char_offset = 0
        
        for line_num, line in enumerate(lines, 1):
            matches = pattern.finditer(line)
            for match in matches:
                raw_value = match.group(0)
                value_lower = raw_value.lower()
                start_idx = match.start()
                
                token_type = TokenType.UNKNOWN
                
                if not raw_value.strip():
                    continue
                
                if re.match(r'^[^\w\s]$', raw_value):
                    token_type = TokenType.PUNCTUATION
                elif value_lower in ENTITY_KEYWORDS:
                    token_type = TokenType.ENTITY
                elif value_lower in ACTION_KEYWORDS:
                    token_type = TokenType.ACTION
                elif value_lower in FEATURE_KEYWORDS:
                    token_type = TokenType.FEATURE
                elif value_lower in ROLE_KEYWORDS:
                    token_type = TokenType.ROLE
                elif value_lower in CONSTRAINT_KEYWORDS:
                    token_type = TokenType.CONSTRAINT
                elif value_lower in PLAN_KEYWORDS:
                    token_type = TokenType.PLAN
                elif value_lower in INTEGRATION_KEYWORDS:
                    token_type = TokenType.INTEGRATION
                elif value_lower in RELATION_KEYWORDS:
                    token_type = TokenType.CONNECTOR
                elif value_lower in MODIFIER_KEYWORDS:
                    token_type = TokenType.MODIFIER
                elif value_lower in {"and", "or"}:
                    token_type = TokenType.CONNECTOR
                elif value_lower in {"multiple", "many", "single"}:
                    token_type = TokenType.QUANTIFIER
                elif value_lower.endswith('s') and value_lower[:-1] in ENTITY_KEYWORDS:
                    # Plural heuristic
                    token_type = TokenType.ENTITY
                    value_lower = value_lower[:-1]
                    
                token = Token(
                    type=token_type,
                    value=value_lower,
                    raw=raw_value,
                    position=char_offset + start_idx,
                    line=line_num,
                    confidence=1.0 if token_type != TokenType.UNKNOWN else 0.5
                )
                tokens.append(token)
            
            char_offset += len(line) + 1 # +1 for newline
            
        if self.use_spacy:
            self._enrich_with_spacy(text, tokens)
            
        return tokens

    def _enrich_with_spacy(self, text: str, tokens: list[Token]):
        doc = self.nlp(text)
        
        # Very basic enrichment for unknown tokens
        # E.g. finding nouns as entities
        for token in tokens:
            if token.type == TokenType.UNKNOWN:
                for spacy_token in doc:
                    if spacy_token.idx == token.position:
                        if spacy_token.pos_ == "NOUN":
                            token.type = TokenType.ENTITY
                            token.confidence = 0.8
                        elif spacy_token.pos_ == "VERB":
                            token.type = TokenType.ACTION
                            token.confidence = 0.8
                        break
