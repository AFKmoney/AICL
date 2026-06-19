"""
AICL Behavior Pattern Library - Deterministic Compilation Engine

This module is the heart of AICL's deterministic compilation. It maps
behavioral descriptions to concrete code through two mechanisms:

1. PATTERN MATCHING: Action descriptions like "Update paddle position"
   are matched to known patterns (MOVE, BROADCAST, CREATE, etc.)
   which produce deterministic, parameterized code.

2. SUB-LANGUAGE: When no pattern matches, users can write explicit
   action statements using AICL's action sub-language:
     assign x += direction * speed
     clamp position between 0 and max
     check score >= 10
     send message to channel

Together, these eliminate TODOs from compiled output.

Design Principle:
    The compiler must be 100% deterministic. Same input -> same output. Always.
    AI-assisted code filling (--ai-fill) is a separate, optional mode.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum


# =============================================================================
# Pattern Categories
# =============================================================================

class PatternCategory(Enum):
    """Categories of behavior patterns."""
    MOVEMENT = "movement"
    CREATION = "creation"
    DELETION = "deletion"
    UPDATE = "update"
    TRANSFORM = "transform"
    FILTER = "filter"
    SORT = "sort"
    ROUTE = "route"
    BROADCAST = "broadcast"
    VALIDATE = "validate"
    ENCRYPT = "encrypt"
    SERIALIZE = "serialize"
    DESERIALIZE = "deserialize"
    STORE = "store"
    LOAD = "load"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    DISPLAY = "display"
    NOTIFY = "notify"
    LOG = "log"
    CLAMP = "clamp"
    REFLECT = "reflect"
    INITIALIZE = "initialize"
    RENDER = "render"
    SYNC = "sync"
    BUFFER = "buffer"
    QUEUE = "queue"
    RETRY = "retry"
    TIMEOUT = "timeout"
    ADAPT = "adapt"


# =============================================================================
# Pattern Match Result
# =============================================================================

@dataclass
class PatternMatch:
    """Result of matching an action description to a pattern."""
    pattern_name: str
    category: PatternCategory
    confidence: float  # 0.0 to 1.0
    parameters: Dict[str, str] = field(default_factory=dict)
    code_template: str = ""  # Python code template with {param} placeholders


# =============================================================================
# Sub-Language Statement
# =============================================================================

class SubLangType(Enum):
    ASSIGN = "assign"
    CLAMP = "clamp"
    CHECK = "check"
    SEND = "send"
    RETURN = "return"
    CALL = "call"
    LOG = "log"
    RAISE = "raise"


@dataclass
class SubLangStatement:
    """A parsed sub-language statement."""
    statement_type: SubLangType
    raw: str = ""
    target: str = ""       # variable/attribute being operated on
    operator: str = ""     # +=, -=, =, etc.
    value: str = ""        # right-hand side expression
    min_val: str = ""      # for clamp
    max_val: str = ""      # for clamp
    condition: str = ""    # for check
    destination: str = ""  # for send
    message: str = ""      # for send/log


# =============================================================================
# Behavior Pattern Library
# =============================================================================

class BehaviorPatternLibrary:
    """
    Library of deterministic behavior patterns.

    Each pattern maps a semantic intent (described via keywords)
    to a parameterized Python code template. Pattern matching
    is keyword-based, not AI-based.
    """

    def __init__(self):
        self._patterns: List[Dict] = []
        self._register_builtin_patterns()

    def _register_builtin_patterns(self):
        """Register all built-in behavior patterns."""

        # ── Movement / Position ──────────────────────────────────────────

        self._add_pattern(
            name="MOVE",
            category=PatternCategory.MOVEMENT,
            keywords=["move", "update position", "move paddle", "update paddle",
                       "change position", "shift", "translate", "reposition"],
            parameters=["entity", "position_attr", "direction", "speed"],
            template=(
                "if {direction} is not None:\n"
                "    {entity}.{position_attr} += {direction} * {speed}\n"
                "    self._logger.info(f\"Moved {entity}: {position_attr} = {{{entity}.{position_attr}}}\")"
            ),
        )

        self._add_pattern(
            name="MOVE_BALL",
            category=PatternCategory.MOVEMENT,
            keywords=["update ball position", "move ball", "ball movement", "ball movement and collision"],
            parameters=["entity", "x_attr", "y_attr", "vx_attr", "vy_attr", "dt"],
            template=(
                "{entity}.{x_attr} += {entity}.{vx_attr} * {dt}\n"
                "{entity}.{y_attr} += {entity}.{vy_attr} * {dt}\n"
                "self._logger.debug(f\"Ball at ({{{entity}.{x_attr}}}, {{{entity}.{y_attr}}})\")"
            ),
        )

        self._add_pattern(
            name="REFLECT_VELOCITY",
            category=PatternCategory.REFLECT,
            keywords=["reflect", "bounce", "reflect velocity", "reverse direction"],
            parameters=["entity", "axis"],
            template=(
                "if \"{axis}\" == \"x\" or \"{axis}\" == \"horizontal\":\n"
                "    {entity}.velocity_x = -{entity}.velocity_x\n"
                "elif \"{axis}\" == \"y\" or \"{axis}\" == \"vertical\":\n"
                "    {entity}.velocity_y = -{entity}.velocity_y\n"
                "else:\n"
                "    {entity}.velocity_x = -{entity}.velocity_x\n"
                "    {entity}.velocity_y = -{entity}.velocity_y\n"
                "self._logger.info(f\"Reflected {entity} velocity on {axis} axis\")"
            ),
        )

        self._add_pattern(
            name="CLAMP_POSITION",
            category=PatternCategory.CLAMP,
            keywords=["clamp", "constrain", "limit position", "clamp position", "bound",
                       "keep within", "restrict to", "boundary"],
            parameters=["entity", "attr", "min_val", "max_val"],
            template=(
                "if {entity}.{attr} < {min_val}:\n"
                "    {entity}.{attr} = {min_val}\n"
                "elif {entity}.{attr} > {max_val}:\n"
                "    {entity}.{attr} = {max_val}\n"
                "self._logger.debug(f\"Clamped {entity}.{attr} to [{min_val}, {max_val}]\")"
            ),
        )

        # ── Creation / Initialization ────────────────────────────────────

        self._add_pattern(
            name="CREATE",
            category=PatternCategory.CREATION,
            keywords=["create", "initialize", "instantiate", "new", "setup", "build",
                       "make", "construct", "prepare", "open"],
            parameters=["entity_type", "init_args"],
            template=(
                "instance = {entity_type}({init_args})\n"
                "self._logger.info(f\"Created {entity_type}: {{instance}}\")\n"
                "return instance"
            ),
        )

        self._add_pattern(
            name="INIT_LAYER",
            category=PatternCategory.INITIALIZE,
            keywords=["init", "initialize layer", "setup layer", "start layer", "create layer"],
            parameters=["layer_name", "sublayers"],
            template=(
                "component = {{\n"
                "    'name': '{layer_name}',\n"
                "    'active': True,\n"
                "    'sublayers': {sublayers},\n"
                "}}\n"
                "self._logger.info(f\"Initialized layer: {layer_name}\")\n"
                "return component"
            ),
        )

        # ── Communication ────────────────────────────────────────────────

        self._add_pattern(
            name="BROADCAST",
            category=PatternCategory.BROADCAST,
            keywords=["broadcast", "transmit", "send to all", "publish", "announce",
                       "notify all", "distribute"],
            parameters=["message", "channel", "recipients"],
            template=(
                "for recipient in {recipients}:\n"
                "    self._send_to(recipient, {message})\n"
                "self._logger.info(f\"Broadcast to {{len({recipients})}} recipients\")"
            ),
        )

        self._add_pattern(
            name="SEND_MESSAGE",
            category=PatternCategory.ROUTE,
            keywords=["send message", "transmit message", "deliver message", "route message",
                       "forward message", "dispatch"],
            parameters=["message", "destination", "channel"],
            template=(
                "self._send_to({destination}, {message})\n"
                "self._logger.info(f\"Sent message to {destination}\")"
            ),
        )

        # ── Update / Modify ──────────────────────────────────────────────

        self._add_pattern(
            name="UPDATE",
            category=PatternCategory.UPDATE,
            keywords=["update", "modify", "set", "change", "increment", "decrement",
                       "adjust", "increase", "decrease", "toggle"],
            parameters=["entity", "attr", "value"],
            template=(
                "{entity}.{attr} = {value}\n"
                "self._logger.info(f\"Updated {entity}.{attr} = {{{entity}.{attr}}}\")"
            ),
        )

        self._add_pattern(
            name="INCREMENT_SCORE",
            category=PatternCategory.UPDATE,
            keywords=["increment score", "update score", "add score", "score increment",
                       "increment point", "add point", "score tracking"],
            parameters=["entity", "score_attr", "amount"],
            template=(
                "{entity}.{score_attr} += {amount}\n"
                "self._logger.info(f\"Score: {{{entity}.{score_attr}}}\")"
            ),
        )

        self._add_pattern(
            name="ADD_TO_COLLECTION",
            category=PatternCategory.UPDATE,
            keywords=["add", "append", "insert", "push", "join", "add user",
                       "add to", "join channel", "add member"],
            parameters=["collection", "item"],
            template=(
                "{collection}.append({item})\n"
                "self._logger.info(f\"Added {{item}} to {collection}\")"
            ),
        )

        self._add_pattern(
            name="REMOVE_FROM_COLLECTION",
            category=PatternCategory.DELETION,
            keywords=["remove", "delete", "pop", "remove from", "leave", "disconnect",
                       "remove user", "remove member"],
            parameters=["collection", "item"],
            template=(
                "if {item} in {collection}:\n"
                "    {collection}.remove({item})\n"
                "    self._logger.info(f\"Removed {{item}} from {collection}\")"
            ),
        )

        # ── Display / Rendering ──────────────────────────────────────────

        self._add_pattern(
            name="DISPLAY",
            category=PatternCategory.DISPLAY,
            keywords=["display", "show", "render", "draw", "paint", "visualize",
                       "print", "output"],
            parameters=["content", "target"],
            template=(
                "self._render({content}, target={target})\n"
                "self._logger.debug(f\"Displayed content to {target}\")"
            ),
        )

        self._add_pattern(
            name="RENDER_FRAME",
            category=PatternCategory.RENDER,
            keywords=["render frame", "render scene", "draw frame", "render sprite",
                       "render text", "render background", "draw screen", "update display"],
            parameters=["elements", "target"],
            template=(
                "for element in {elements}:\n"
                "    self._draw_element(element)\n"
                "self._flush_display()\n"
                "self._logger.debug(\"Rendered frame\")"
            ),
        )

        # ── Validation / Checking ────────────────────────────────────────

        self._add_pattern(
            name="VALIDATE",
            category=PatternCategory.VALIDATE,
            keywords=["validate", "verify", "check", "ensure", "confirm", "assert",
                       "test", "inspect"],
            parameters=["condition", "error_msg"],
            template=(
                "result = {condition}\n"
                "if not result:\n"
                "    self._logger.warning('Validation failed: {error_msg}')\n"
                "return result"
            ),
        )

        self._add_pattern(
            name="CHECK_COLLISION",
            category=PatternCategory.VALIDATE,
            keywords=["collision", "detect collision", "check collision", "hit test",
                       "overlap", "intersect"],
            parameters=["entity_a", "entity_b", "threshold"],
            template=(
                "dx = {entity_a}.x - {entity_b}.x\n"
                "dy = {entity_a}.y - {entity_b}.y\n"
                "distance = (dx * dx + dy * dy) ** 0.5\n"
                "collision = distance < {threshold}\n"
                "if collision:\n"
                "    self._logger.info(f\"Collision detected between {entity_a} and {entity_b}\")\n"
                "return collision"
            ),
        )

        # ── Networking / Connection ──────────────────────────────────────

        self._add_pattern(
            name="CONNECT",
            category=PatternCategory.CONNECT,
            keywords=["connect", "establish connection", "open connection", "dial",
                       "link", "attach"],
            parameters=["host", "port"],
            template=(
                "self._connection = self._create_connection({host}, {port})\n"
                "self._logger.info(f\"Connected to {host}:{port}\")\n"
                "return self._connection"
            ),
        )

        self._add_pattern(
            name="RECONNECT",
            category=PatternCategory.RETRY,
            keywords=["reconnect", "retry connection", "re-establish", "restore connection",
                       "reconnect automatically", "retry"],
            parameters=["host", "port", "max_retries"],
            template=(
                "for attempt in range({max_retries}):\n"
                "    try:\n"
                "        self._connection = self._create_connection({host}, {port})\n"
                "        self._logger.info(f\"Reconnected on attempt {{attempt + 1}}\")\n"
                "        return self._connection\n"
                "    except Exception as e:\n"
                "        wait_time = 2 ** attempt\n"
                "        self._logger.warning(f\"Retry {{attempt + 1}}/{{{max_retries}}} failed: {{e}}\")\n"
                "        time.sleep(wait_time)\n"
                "self._logger.error(\"All reconnection attempts failed\")\n"
                "return None"
            ),
        )

        self._add_pattern(
            name="DISCONNECT",
            category=PatternCategory.DISCONNECT,
            keywords=["disconnect", "close connection", "terminate", "detach",
                       "go offline", "shut down"],
            parameters=["connection"],
            template=(
                "if {connection} is not None:\n"
                "    {connection}.close()\n"
                "    {connection} = None\n"
                "    self._logger.info(\"Disconnected\")"
            ),
        )

        # ── Persistence ──────────────────────────────────────────────────

        self._add_pattern(
            name="STORE",
            category=PatternCategory.STORE,
            keywords=["store", "save", "persist", "write", "record", "archive",
                       "cache", "commit"],
            parameters=["data", "location"],
            template=(
                "self._storage[{location!r}] = {data}\n"
                "self._logger.info(f\"Stored data at {location}\")"
            ),
        )

        self._add_pattern(
            name="LOAD",
            category=PatternCategory.LOAD,
            keywords=["load", "read", "fetch", "retrieve", "get", "open",
                       "restore"],
            parameters=["location", "default"],
            template=(
                "data = self._storage.get({location!r}, {default})\n"
                "self._logger.info(f\"Loaded data from {location}\")\n"
                "return data"
            ),
        )

        # ── Security ─────────────────────────────────────────────────────

        self._add_pattern(
            name="ENCRYPT_DATA",
            category=PatternCategory.ENCRYPT,
            keywords=["encrypt", "cipher", "encode securely", "protect data"],
            parameters=["data", "key"],
            template=(
                "encrypted = self._encrypt({data}, key={key})\n"
                "self._logger.info(f\"Encrypted {data}\")\n"
                "return encrypted"
            ),
        )

        self._add_pattern(
            name="PROTECT_ACCESS",
            category=PatternCategory.VALIDATE,
            keywords=["protect", "guard", "secure", "restrict access", "authenticate",
                       "authorize", "protect credentials"],
            parameters=["resource", "role"],
            template=(
                "if not self._check_access({resource}, role={role}):\n"
                "    raise PermissionError(f\"Access denied for {resource}\")\n"
                "self._logger.info(f\"Access granted to {resource}\")"
            ),
        )

        # ── Concurrency / Sync ───────────────────────────────────────────

        self._add_pattern(
            name="SYNC_STATE",
            category=PatternCategory.SYNC,
            keywords=["sync", "synchronize", "sync offline", "merge", "reconcile",
                       "sync offline messages", "synchronize state"],
            parameters=["local_state", "remote_state"],
            template=(
                "pending = self._{local_state}.get('pending', [])\n"
                "for item in pending:\n"
                "    self._send_to({remote_state}, item)\n"
                "self._{local_state}['pending'] = []\n"
                "self._logger.info(f\"Synced {{len(pending)}} items\")"
            ),
        )

        self._add_pattern(
            name="BUFFER_INPUT",
            category=PatternCategory.BUFFER,
            keywords=["buffer", "queue input", "input buffer", "enable buffer",
                       "enable input buffering", "cache input"],
            parameters=["input_stream", "buffer_size"],
            template=(
                "self._input_buffer = []\n"
                "self._buffer_size = {buffer_size}\n"
                "self._buffering = True\n"
                "self._logger.info(f\"Input buffering enabled (size={buffer_size})\")"
            ),
        )

        # ── Notifications ────────────────────────────────────────────────

        self._add_pattern(
            name="NOTIFY",
            category=PatternCategory.NOTIFY,
            keywords=["notify", "alert", "inform", "signal", "emit", "fire event",
                       "notify members", "update user list"],
            parameters=["recipients", "message"],
            template=(
                "for recipient in {recipients}:\n"
                "    self._notify(recipient, {message})\n"
                "self._logger.info(f\"Notified {{len({recipients})}} recipients\")"
            ),
        )

        # ── Game Logic ───────────────────────────────────────────────────

        self._add_pattern(
            name="END_GAME",
            category=PatternCategory.UPDATE,
            keywords=["end game", "end match", "game over", "declare winner",
                       "end round", "finish", "complete game", "end match"],
            parameters=["winner", "final_state"],
            template=(
                "self._game_active = False\n"
                "self._winner = {winner}\n"
                "self._logger.info(f\"Game over. Winner: {{{winner}}}\")\n"
                "return {final_state}"
            ),
        )

        self._add_pattern(
            name="HIGHLIGHT",
            category=PatternCategory.DISPLAY,
            keywords=["highlight", "emphasize", "mark", "select", "indicate",
                       "show valid moves", "highlight valid", "highlight threatened"],
            parameters=["targets", "style"],
            template=(
                "for target in {targets}:\n"
                "    target.highlighted = True\n"
                "    target.highlight_style = \"{style}\"\n"
                "self._logger.info(f\"Highlighted {{len({targets})}} items\")"
            ),
        )

        # ── Adaptation ───────────────────────────────────────────────────

        self._add_pattern(
            name="ADAPT_QUALITY",
            category=PatternCategory.ADAPT,
            keywords=["adapt", "adjust quality", "scale quality", "reduce quality",
                       "graphics quality", "quality level", "adapt graphics"],
            parameters=["metric", "threshold_low", "threshold_high"],
            template=(
                "current = self._measure({metric})\n"
                "if current < {threshold_low}:\n"
                "    self._quality_level = max(1, self._quality_level - 1)\n"
                "    self._logger.info(f\"Reduced quality to {{self._quality_level}}\")\n"
                "elif current > {threshold_high}:\n"
                "    self._quality_level = min(10, self._quality_level + 1)\n"
                "    self._logger.info(f\"Increased quality to {{self._quality_level}}\")"
            ),
        )

        # ── Offline / Queue ──────────────────────────────────────────────

        self._add_pattern(
            name="QUEUE_MESSAGE",
            category=PatternCategory.QUEUE,
            keywords=["queue", "enqueue", "store locally", "store for later",
                       "offline queue", "store locally and retry", "pending"],
            parameters=["message", "queue_name"],
            template=(
                "self._{queue_name}.append({message})\n"
                "self._logger.info(f\"Queued message in {queue_name} (size={{len(self._{queue_name})}})\")"
            ),
        )

        # ── Game State Management ────────────────────────────────────────

        self._add_pattern(
            name="UPDATE_STATE",
            category=PatternCategory.UPDATE,
            keywords=["update state", "update board", "change state", "set state",
                       "update board state", "game state management", "manage state",
                       "round management"],
            parameters=["entity", "attr", "new_value"],
            template=(
                "{entity}.{attr} = {new_value}\n"
                "self._logger.info(f\"State updated: {entity}.{attr} = {{{entity}.{attr}}}\")"
            ),
        )

        # ── Physics ──────────────────────────────────────────────────────

        self._add_pattern(
            name="APPLY_PHYSICS",
            category=PatternCategory.MOVEMENT,
            keywords=["apply physics", "physics", "physics reflection",
                       "apply physics reflection", "handle physics", "calculate physics"],
            parameters=["entity", "surface_normal"],
            template=(
                "# Apply physics reflection\n"
                "dot = {entity}.velocity_x * {surface_normal}[0] + {entity}.velocity_y * {surface_normal}[1]\n"
                "{entity}.velocity_x -= 2 * dot * {surface_normal}[0]\n"
                "{entity}.velocity_y -= 2 * dot * {surface_normal}[1]\n"
                "self._logger.info(f\"Applied physics reflection to {entity}\")"
            ),
        )

        # ── Suggestion / Learning ────────────────────────────────────────

        self._add_pattern(
            name="SUGGEST",
            category=PatternCategory.ADAPT,
            keywords=["suggest", "recommend", "improve", "improve message",
                       "message suggestion", "auto-complete", "predict"],
            parameters=["context", "suggestions_attr"],
            template=(
                "recent = getattr(self, '{suggestions_attr}', [])[-5:]\n"
                "self._suggestions = self._generate_suggestions(recent)\n"
                "self._logger.info(f\"Generated {{len(self._suggestions)}} suggestions\")"
            ),
        )

        # ── Heartbeat / Keepalive ────────────────────────────────────────

        self._add_pattern(
            name="HEARTBEAT",
            category=PatternCategory.NOTIFY,
            keywords=["heartbeat", "keepalive", "ping", "health check", "alive check"],
            parameters=["interval", "target"],
            template=(
                "self._last_heartbeat = time.time()\n"
                "self._send_to({target}, {'type': 'heartbeat', 'timestamp': self._last_heartbeat})\n"
                "self._logger.debug(\"Heartbeat sent\")"
            ),
        )

        # ── Window Management ────────────────────────────────────────────

        self._add_pattern(
            name="CREATE_WINDOW",
            category=PatternCategory.CREATION,
            keywords=["window", "create window", "open window", "display window",
                       "application window", "window manager"],
            parameters=["width", "height", "title"],
            template=(
                "component = {{\n"
                "    'name': '{title}',\n"
                "    'width': {width},\n"
                "    'height': {height},\n"
                "    'active': True,\n"
                "}}\n"
                "self._logger.info(f\"Window created: {title} ({width}x{height})\")\n"
                "return component"
            ),
        )

    def _add_pattern(
        self,
        name: str,
        category: PatternCategory,
        keywords: List[str],
        parameters: List[str],
        template: str,
    ):
        """Register a behavior pattern."""
        self._patterns.append({
            'name': name,
            'category': category,
            'keywords': keywords,
            'parameters': parameters,
            'template': template,
        })

    # =========================================================================
    # Pattern Matching
    # =========================================================================

    def match(self, action_description: str) -> Optional[PatternMatch]:
        """
        Match an action description to a known pattern.

        Uses keyword matching (not AI). The matching algorithm:
        1. Normalize the description to lowercase
        2. Check each pattern's keywords against the description
        3. Return the best match (most keyword hits)

        Returns None if no pattern matches with confidence > 0.3.
        """
        if not action_description or not action_description.strip():
            return None

        desc_lower = action_description.lower().strip()
        best_match = None
        best_score = 0.0

        for pattern in self._patterns:
            score = self._score_pattern(desc_lower, pattern['keywords'])
            if score > best_score:
                best_score = score
                best_match = pattern

        if best_match and best_score > 0.3:
            # Extract parameters from context
            params = self._extract_parameters(
                action_description, best_match['parameters']
            )
            return PatternMatch(
                pattern_name=best_match['name'],
                category=best_match['category'],
                confidence=best_score,
                parameters=params,
                code_template=best_match['template'],
            )

        return None

    def _word_in_text(self, word: str, text: str) -> bool:
        """Check if a word appears as a whole word in text (not as substring)."""
        pattern = r'\b' + re.escape(word) + r'\b'
        return bool(re.search(pattern, text))

    def _score_pattern(self, desc_lower: str, keywords: List[str]) -> float:
        """
        Score how well a description matches a pattern's keywords.

        Uses word-boundary matching to avoid false positives
        (e.g., "play" matching inside "multiplayer").
        """
        if not keywords:
            return 0.0

        matches = 0
        for kw in keywords:
            kw_lower = kw.lower()
            # For multi-word keywords, check if the phrase appears
            if ' ' in kw_lower:
                if kw_lower in desc_lower:
                    word_count = len(kw_lower.split())
                    matches += word_count
                elif any(self._word_in_text(w, desc_lower) for w in kw_lower.split() if len(w) > 3):
                    matches += 0.3
            else:
                # Single-word keyword: use word-boundary matching
                if self._word_in_text(kw_lower, desc_lower):
                    matches += 1

        # Normalize: best single keyword match gets 1.0
        max_possible = max(len(kw.split()) for kw in keywords)
        score = min(matches / max(max_possible, 1), 1.0)

        # Bonus for exact phrase match
        for kw in keywords:
            if ' ' in kw.lower() and kw.lower() in desc_lower:
                score = min(score + 0.2, 1.0)
                break
            elif ' ' not in kw.lower() and self._word_in_text(kw.lower(), desc_lower):
                score = min(score + 0.2, 1.0)
                break

        return score

    def _extract_parameters(
        self, description: str, param_names: List[str]
    ) -> Dict[str, str]:
        """
        Extract parameter values from an action description.

        Uses heuristics to fill common parameters with sensible defaults.
        For production, these would come from the AICL program context
        (entity names, field names, etc.).
        """
        params = {}
        desc_lower = description.lower()

        for param in param_names:
            if param == "entity":
                params[param] = self._guess_entity(desc_lower)
            elif param in ("position_attr", "attr"):
                params[param] = self._guess_attr(desc_lower, param)
            elif param == "direction":
                params[param] = "direction"
            elif param == "speed":
                params[param] = "5"
            elif param == "dt":
                params[param] = "1.0"
            elif param in ("x_attr", "y_attr"):
                params[param] = param.replace("_attr", "")
            elif param in ("vx_attr", "vy_attr"):
                params[param] = param.replace("_attr", "")
            elif param == "axis":
                params[param] = self._guess_axis(desc_lower)
            elif param == "min_val":
                params[param] = "0"
            elif param == "max_val":
                params[param] = "800"
            elif param in ("host", "port"):
                params[param] = '"localhost"' if param == "host" else "8080"
            elif param == "max_retries":
                params[param] = "3"
            elif param == "buffer_size":
                params[param] = "100"
            elif param == "threshold":
                params[param] = "10"
            elif param in ("width", "height"):
                params[param] = "800" if param == "width" else "600"
            elif param == "title":
                params[param] = '"AICL Application"'
            elif param == "amount":
                params[param] = "1"
            elif param == "channel":
                params[param] = "self._current_channel"
            elif param == "recipients":
                params[param] = "self._users"
            elif param == "message":
                params[param] = "msg"
            elif param == "destination":
                params[param] = "self._server"
            elif param == "content":
                params[param] = "data"
            elif param == "target":
                params[param] = "self._display"
            elif param == "elements":
                params[param] = "self._render_queue"
            elif param == "condition":
                params[param] = "True"
            elif param == "error_msg":
                params[param] = '"Validation failed"'
            elif param == "data":
                params[param] = "data"
            elif param == "location":
                params[param] = "'default'"
            elif param == "default":
                params[param] = "None"
            elif param == "key":
                params[param] = "self._encryption_key"
            elif param == "resource":
                params[param] = "resource"
            elif param == "role":
                params[param] = "'user'"
            elif param == "winner":
                params[param] = "self._winner"
            elif param == "final_state":
                params[param] = "self._state"
            elif param == "entity_a":
                params[param] = "entity_a"
            elif param == "entity_b":
                params[param] = "entity_b"
            elif param == "entity_type":
                params[param] = "cls"
            elif param == "init_args":
                params[param] = ""
            elif param == "layer_name":
                params[param] = description.strip().title()
            elif param == "sublayers":
                params[param] = "[]"
            elif param == "local_state":
                params[param] = "offline_queue"
            elif param == "remote_state":
                params[param] = "server"
            elif param == "input_stream":
                params[param] = "input_stream"
            elif param == "queue_name":
                params[param] = "message_queue"
            elif param == "collection":
                params[param] = "items"
            elif param == "item":
                params[param] = "item"
            elif param == "value":
                params[param] = "value"
            elif param == "new_value":
                params[param] = "new_value"
            elif param == "surface_normal":
                params[param] = "[0, 1]"
            elif param == "targets":
                params[param] = "targets"
            elif param == "style":
                params[param] = "default"
            elif param == "metric":
                params[param] = "'fps'"
            elif param in ("threshold_low", "threshold_high"):
                params[param] = "30" if "low" in param else "60"
            elif param == "context":
                params[param] = "context"
            elif param == "suggestions_attr":
                params[param] = "suggestions"
            elif param == "connection":
                params[param] = "self._connection"
            elif param == "interval":
                params[param] = "30"
            else:
                params[param] = f"#{param}#"

        return params

    def _guess_entity(self, desc_lower: str) -> str:
        """Guess the entity name from the description."""
        entity_hints = {
            "ball": "self._ball", "paddle": "self._player", "player": "self._player",
            "message": "self._message", "user": "self._user", "piece": "self._chess_piece",
            "game": "self._game_state", "state": "self._game_state", "board": "self._game_state",
            "window": "component", "renderer": "component",
        }
        for hint, entity in entity_hints.items():
            if hint in desc_lower:
                return entity
        return "self._entity"

    def _guess_attr(self, desc_lower: str, param_name: str) -> str:
        """Guess the attribute name from the description."""
        attr_hints = {
            "position": "position", "score": "score", "x": "x",
            "y": "y", "velocity": "velocity", "paddle": "paddle_position",
            "state": "state", "turn": "current_turn", "status": "status",
        }
        for hint, attr in attr_hints.items():
            if hint in desc_lower:
                return attr
        return param_name

    def _guess_axis(self, desc_lower: str) -> str:
        """Guess the reflection axis from the description."""
        if "horizontal" in desc_lower or "x" in desc_lower:
            return "x"
        elif "vertical" in desc_lower or "y" in desc_lower:
            return "y"
        return "both"


# =============================================================================
# Sub-Language Parser
# =============================================================================

class SubLanguageParser:
    """
    Parser for AICL's action sub-language.

    The sub-language allows explicit, deterministic specification of
    behavior when no pattern matches. It provides a small set of
    composable statements:

        assign <target> <op> <expr>     # e.g., assign x += direction * speed
        clamp <target> between <min> and <max>
        check <condition>               # e.g., check score >= 10
        send <message> to <destination>
        return <expr>
        call <method>(<args>)
        log <message>
        raise <exception>

    Grammar (BNF):
        <stmt_list>  ::= <stmt> (NEWLINE <stmt>)*
        <stmt>       ::= <assign_stmt> | <clamp_stmt> | <check_stmt>
                       | <send_stmt> | <return_stmt> | <call_stmt>
                       | <log_stmt> | <raise_stmt>
        <assign_stmt>::= "assign" <target> <assign_op> <expr>
        <clamp_stmt> ::= "clamp" <target> "between" <expr> "and" <expr>
        <check_stmt> ::= "check" <condition>
        <send_stmt>  ::= "send" <expr> "to" <expr>
        <return_stmt>::= "return" <expr>
        <call_stmt>  ::= "call" <identifier> "(" <args>? ")"
        <log_stmt>   ::= "log" <expr>
        <raise_stmt> ::= "raise" <expr>
        <assign_op>  ::= "=" | "+=" | "-=" | "*=" | "/="
        <expr>       ::= <any Python expression>
        <target>     ::= <identifier> ("." <identifier>)*
    """

    KEYWORDS = {'assign', 'clamp', 'check', 'send', 'return', 'call', 'log', 'raise'}

    def parse(self, action_text: str) -> List[SubLangStatement]:
        """
        Parse action text into sub-language statements.

        Returns a list of SubLangStatement. If the text doesn't contain
        any sub-language keywords, returns an empty list (indicating the
        text should be passed to the pattern matcher instead).
        """
        statements = []
        lines = action_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            stmt = self._parse_line(line)
            if stmt:
                statements.append(stmt)

        return statements

    def _parse_line(self, line: str) -> Optional[SubLangStatement]:
        """Parse a single line of sub-language."""
        line_lower = line.lower()

        if line_lower.startswith('assign '):
            return self._parse_assign(line[7:].strip())
        elif line_lower.startswith('clamp '):
            return self._parse_clamp(line[6:].strip())
        elif line_lower.startswith('check '):
            return self._parse_check(line[6:].strip())
        elif line_lower.startswith('send '):
            return self._parse_send(line[5:].strip())
        elif line_lower.startswith('return '):
            return self._parse_return(line[7:].strip())
        elif line_lower.startswith('call '):
            return self._parse_call(line[5:].strip())
        elif line_lower.startswith('log '):
            return self._parse_log(line[4:].strip())
        elif line_lower.startswith('raise '):
            return self._parse_raise(line[6:].strip())

        return None

    def _parse_assign(self, text: str) -> SubLangStatement:
        """Parse: assign target op expr"""
        # Try compound assignment operators first
        for op in ['+=', '-=', '*=', '/=', '//=', '%=', '**=', '=']:
            if op in text:
                parts = text.split(op, 1)
                if len(parts) == 2:
                    return SubLangStatement(
                        statement_type=SubLangType.ASSIGN,
                        raw=text,
                        target=parts[0].strip(),
                        operator=op,
                        value=parts[1].strip(),
                    )
        return SubLangStatement(
            statement_type=SubLangType.ASSIGN,
            raw=text,
            target=text,
            operator="=",
            value="None",
        )

    def _parse_clamp(self, text: str) -> SubLangStatement:
        """Parse: clamp target between min and max"""
        # "paddle_position between 0 and screen_height"
        match = re.match(
            r'(\S+)\s+between\s+(.+?)\s+and\s+(.+)',
            text, re.IGNORECASE
        )
        if match:
            return SubLangStatement(
                statement_type=SubLangType.CLAMP,
                raw=text,
                target=match.group(1).strip(),
                min_val=match.group(2).strip(),
                max_val=match.group(3).strip(),
            )
        return SubLangStatement(
            statement_type=SubLangType.CLAMP,
            raw=text,
            target=text,
            min_val="0",
            max_val="MAX_VALUE",
        )

    def _parse_check(self, text: str) -> SubLangStatement:
        """Parse: check condition"""
        return SubLangStatement(
            statement_type=SubLangType.CHECK,
            raw=text,
            condition=text,
        )

    def _parse_send(self, text: str) -> SubLangStatement:
        """Parse: send message to destination"""
        match = re.match(
            r'(.+?)\s+to\s+(.+)',
            text, re.IGNORECASE
        )
        if match:
            return SubLangStatement(
                statement_type=SubLangType.SEND,
                raw=text,
                message=match.group(1).strip(),
                destination=match.group(2).strip(),
            )
        return SubLangStatement(
            statement_type=SubLangType.SEND,
            raw=text,
            message=text,
            destination="recipient",
        )

    def _parse_return(self, text: str) -> SubLangStatement:
        """Parse: return expr"""
        return SubLangStatement(
            statement_type=SubLangType.RETURN,
            raw=text,
            value=text,
        )

    def _parse_call(self, text: str) -> SubLangStatement:
        """Parse: call method(args)"""
        return SubLangStatement(
            statement_type=SubLangType.CALL,
            raw=text,
            target=text,
        )

    def _parse_log(self, text: str) -> SubLangStatement:
        """Parse: log message"""
        return SubLangStatement(
            statement_type=SubLangType.LOG,
            raw=text,
            message=text,
        )

    def _parse_raise(self, text: str) -> SubLangStatement:
        """Parse: raise exception"""
        return SubLangStatement(
            statement_type=SubLangType.RAISE,
            raw=text,
            message=text,
        )

    def is_sub_language(self, action_text: str) -> bool:
        """
        Check if action text contains sub-language statements.

        A sub-language statement must be a deliberate instruction, not a
        natural language description that happens to start with a keyword.
        We require the keyword to be followed by a valid sub-language
        construct (not just any text).

        For 'assign': must contain an assignment operator (=, +=, -=, etc.)
        For 'clamp': must contain the word 'between'
        For 'check': must contain a comparison operator (>=, <=, ==, !=, >, <)
        For 'send': must contain the word 'to'
        For 'return', 'call', 'log', 'raise': always treated as sub-language
        """
        for line in action_text.strip().split('\n'):
            line_stripped = line.strip().lower()
            if not line_stripped:
                continue

            if line_stripped.startswith('assign ') and any(op in line_stripped for op in ['+=', '-=', '*=', '/=', '//=', '%=', '**=', ' = ']):
                return True
            elif line_stripped.startswith('clamp ') and 'between' in line_stripped:
                return True
            elif line_stripped.startswith('check ') and any(op in line_stripped for op in ['>=', '<=', '==', '!=', '>', '<']):
                return True
            elif line_stripped.startswith('send ') and ' to ' in line_stripped:
                return True
            elif line_stripped.startswith('return '):
                return True
            elif line_stripped.startswith('call '):
                return True
            elif line_stripped.startswith('log '):
                return True
            elif line_stripped.startswith('raise '):
                return True

        return False


# =============================================================================
# Code Generator from Pattern/Sub-Language
# =============================================================================

class BehaviorCompiler:
    """
    Compiles AICL Behavior sections into deterministic Python code.

    Resolution order:
    1. Sub-language statements (explicit, highest priority)
    2. Pattern matching (keyword-based, deterministic)
    3. Fallback: structured skeleton with semantic comments
       (NOT a bare TODO — a commented implementation outline)
    """

    def __init__(self):
        self.pattern_library = BehaviorPatternLibrary()
        self.sub_lang_parser = SubLanguageParser()

    def compile_action(
        self,
        action_description: str,
        context: Optional[Dict] = None,
    ) -> Tuple[str, bool]:
        """
        Compile an action description into Python code.

        Args:
            action_description: The Action: text from an AICL Behavior
            context: Optional context (entity names, field names, etc.)

        Returns:
            Tuple of (generated_code, is_fully_compiled)
            is_fully_compiled is True if no TODOs remain.
        """
        if not action_description or not action_description.strip():
            return "pass", True

        context = context or {}

        # 1. Try sub-language first
        if self.sub_lang_parser.is_sub_language(action_description):
            stmts = self.sub_lang_parser.parse(action_description)
            if stmts:
                code = self._compile_sub_language(stmts, context)
                # Validate: sub-language patterns can false-positive on prose
                # (e.g. "Return an empty array immediately" matches the `return`
                # keyword but the rest isn't a valid expression). Reject anything
                # that isn't parseable Python and fall through to the fallback.
                if self._is_valid_python(code):
                    return code, True

        # 2. Try pattern matching
        match = self.pattern_library.match(action_description)
        if match and match.confidence > 0.3:
            # Merge context parameters over defaults
            params = match.parameters.copy()
            if context:
                for key, value in context.items():
                    if key in params:
                        params[key] = value

            try:
                code = match.code_template.format(**params)
                if self._is_valid_python(code):
                    return code, True
            except (KeyError, IndexError):
                # Template references parameters not available in context;
                # fall back to structured skeleton with semantic guidance
                pass

        # 3. Fallback: structured skeleton with semantic guidance
        code = self._compile_fallback(action_description, context)
        return code, False

    @staticmethod
    def _is_valid_python(code: str) -> bool:
        """Return True if the generated code parses as valid Python.

        Generated code is embedded inside a method body (indented), so we wrap
        it in a dummy function before parsing to get a representative check.
        This guard prevents prose that slipped past keyword detection from being
        emitted as syntactically invalid Python (e.g. ``return an empty array``).
        """
        import ast
        probe = "def _probe(self):\n    " + code.replace("\n", "\n    ")
        try:
            ast.parse(probe)
            return True
        except SyntaxError:
            return False

    def _compile_sub_language(
        self, stmts: List[SubLangStatement], context: Dict
    ) -> str:
        """Compile sub-language statements to Python code."""
        lines = []
        for stmt in stmts:
            if stmt.statement_type == SubLangType.ASSIGN:
                if stmt.operator == '=':
                    lines.append(f"{stmt.target} = {stmt.value}")
                else:
                    lines.append(f"{stmt.target} {stmt.operator} {stmt.value}")

            elif stmt.statement_type == SubLangType.CLAMP:
                lines.append(f"if {stmt.target} < {stmt.min_val}:")
                lines.append(f"    {stmt.target} = {stmt.min_val}")
                lines.append(f"elif {stmt.target} > {stmt.max_val}:")
                lines.append(f"    {stmt.target} = {stmt.max_val}")

            elif stmt.statement_type == SubLangType.CHECK:
                lines.append(f"if not ({stmt.condition}):")
                lines.append(f'    self._logger.warning("Check failed: {stmt.condition}")')
                lines.append(f"    return False")

            elif stmt.statement_type == SubLangType.SEND:
                lines.append(f"self._send_to({stmt.destination}, {stmt.message})")
                lines.append(f'self._logger.info(f"Sent to {stmt.destination}")')

            elif stmt.statement_type == SubLangType.RETURN:
                lines.append(f"return {stmt.value}")

            elif stmt.statement_type == SubLangType.CALL:
                lines.append(f"self.{stmt.target}")

            elif stmt.statement_type == SubLangType.LOG:
                lines.append(f'self._logger.info(f"{stmt.message}")')

            elif stmt.statement_type == SubLangType.RAISE:
                lines.append(f"raise {stmt.message}")

        return '\n'.join(lines)

    def _compile_fallback(
        self, action_description: str, context: Dict
    ) -> str:
        """
        Generate a structured fallback when no pattern matches.

        This is NOT a bare TODO. It produces:
        - A comment describing the intent
        - A structured code skeleton
        - Parameter extraction hints
        - A logging statement
        """
        desc = action_description.strip()
        # Extract verb and object from the description
        words = desc.split()
        verb = words[0].lower() if words else "process"
        obj = ' '.join(words[1:]) if len(words) > 1 else "data"

        lines = [
            f"# Intent: {desc}",
            f"# Verb: {verb}, Object: {obj}",
            f"self._logger.info(f\"Executing: {desc}\")",
        ]

        # Generate verb-specific skeleton
        if verb in ("update", "change", "modify", "set"):
            lines.append(f"# Update: {obj}")
            lines.append(f"# target.{obj.replace(' ', '_')} = new_value")
            lines.append("pass")
        elif verb in ("create", "initialize", "setup", "init"):
            lines.append(f"# Create: {obj}")
            lines.append(f"# instance = {obj.title().replace(' ', '')}()")
            lines.append("pass")
        elif verb in ("delete", "remove", "destroy"):
            lines.append(f"# Delete: {obj}")
            lines.append("pass")
        elif verb in ("validate", "check", "verify"):
            lines.append(f"# Validate: {obj}")
            lines.append("return True")
        elif verb in ("display", "show", "render", "draw"):
            lines.append(f"# Display: {obj}")
            lines.append("pass")
        else:
            lines.append(f"# Process: {desc}")
            lines.append("pass")

        return '\n'.join(lines)


# =============================================================================
# Goal → Architecture Template Mapper
# =============================================================================

class ArchitectureTemplateMapper:
    """
    Maps Goal descriptions to architecture templates.

    This is deterministic keyword matching, not AI. The mapper
    selects a top-level application structure based on keywords
    in the Goal section.
    """

    TEMPLATE_GAME_LOOP = "game_loop"
    TEMPLATE_EVENT_DRIVEN = "event_driven"
    TEMPLATE_PIPELINE = "pipeline"
    TEMPLATE_CRUD = "crud"

    TEMPLATES = {
        TEMPLATE_GAME_LOOP: {
            'keywords': ['game', 'pong', 'chess', 'snake', 'tetris',
                         'arcade', 'level'],
            'structure': 'init → update → render → loop',
            'run_method': 'game_loop',
        },
        TEMPLATE_EVENT_DRIVEN: {
            'keywords': ['chat', 'server', 'real-time', 'websocket', 'event',
                         'message', 'notification', 'subscribe', 'broadcast',
                         'multiplayer', 'application'],
            'structure': 'connect → listen → handle → respond',
            'run_method': 'event_loop',
        },
        TEMPLATE_PIPELINE: {
            'keywords': ['process', 'transform', 'pipeline', 'data', 'etl',
                         'stream', 'batch', 'analyze', 'ingest'],
            'structure': 'ingest → process → output',
            'run_method': 'pipeline',
        },
        TEMPLATE_CRUD: {
            'keywords': ['manage', 'crud', 'admin', 'dashboard', 'catalog',
                         'inventory', 'record', 'entry', 'form'],
            'structure': 'list → create → read → update → delete',
            'run_method': 'crud_loop',
        },
    }

    @classmethod
    def match(cls, goal_description: str) -> Tuple[str, Dict]:
        """
        Match a goal description to an architecture template.

        Returns (template_name, template_info).
        Defaults to event_driven if no match.
        """
        if not goal_description:
            return cls.TEMPLATE_EVENT_DRIVEN, cls.TEMPLATES[cls.TEMPLATE_EVENT_DRIVEN]

        desc_lower = goal_description.lower()
        best_template = cls.TEMPLATE_EVENT_DRIVEN
        best_score = 0

        for template_name, template_info in cls.TEMPLATES.items():
            score = 0
            for kw in template_info['keywords']:
                # Use word-boundary matching to avoid substring false positives
                if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                    score += 1
            if score > best_score:
                best_score = score
                best_template = template_name

        return best_template, cls.TEMPLATES[best_template]
