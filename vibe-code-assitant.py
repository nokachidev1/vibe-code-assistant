#!/usr/bin/env python3
"""

"""

import os
import sys
import argparse
import textwrap

# ── .env loader (no python-dotenv needed) ────────────────────────────────────
def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_dotenv()

# ── Colors ────────────────────────────────────────────────────────────────────
C = {
    "reset":   "\033[0m",
    "bold":    "\033[1m",
    "dim":     "\033[2m",
    "cyan":    "\033[96m",
    "green":   "\033[92m",
    "yellow":  "\033[93m",
    "red":     "\033[91m",
    "magenta": "\033[95m",
    "blue":    "\033[94m",
    "white":   "\033[97m",
}

def c(color, text):
    return f"{C.get(color,'')}{text}{C['reset']}"

# ── AI labels ─────────────────────────────────────────────────────────────────
AI_INFO = {
    "claude": {
        "label":   "Claude ✦",
        "color":   "magenta",
        "env_key": "ANTHROPIC_API_KEY",
        "model":   "claude-opus-4-5",
    },
    "openai": {
        "label":   "OpenAI ⚡",
        "color":   "green",
        "env_key": "OPENAI_API_KEY",
        "model":   "gpt-4o",
    },
    "grok": {
        "label":   "Grok 𝕏",
        "color":   "blue",
        "env_key": "XAI_API_KEY",
        "model":   "grok-3-latest",
    },
    "gemini": {
        "label":   "Gemini ✦",
        "color":   "cyan",
        "env_key": "GEMINI_API_KEY",
        "model":   "gemini-2.0-flash",
    },
}

SYSTEM_PROMPT = (
    "You are a helpful, sharp, and friendly coding assistant. "
    "Answer clearly and concisely. Use code blocks when showing code. "
    "Be direct — no fluff, no filler. You vibe. 🤙"
)

# ── Lazy dependency check ─────────────────────────────────────────────────────
def try_import(module):
    import importlib
    try:
        return importlib.import_module(module)
    except ImportError:
        return None

# ── API callers ───────────────────────────────────────────────────────────────

def call_claude(messages, api_key, model):
    anthropic = try_import("anthropic")
    if not anthropic:
        raise ImportError("pip install anthropic")
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return resp.content[0].text


def call_openai(messages, api_key, model):
    openai = try_import("openai")
    if not openai:
        raise ImportError("pip install openai")
    client = openai.OpenAI(api_key=api_key)
    full_msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    resp = client.chat.completions.create(model=model, messages=full_msgs, max_tokens=2048)
    return resp.choices[0].message.content


def call_grok(messages, api_key, model):
    # Grok uses the OpenAI-compatible API
    openai = try_import("openai")
    if not openai:
        raise ImportError("pip install openai")
    client = openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    full_msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    resp = client.chat.completions.create(model=model, messages=full_msgs, max_tokens=2048)
    return resp.choices[0].message.content


def call_gemini(messages, api_key, model):
    # Use google-genai SDK
    genai = try_import("google.generativeai")
    if not genai:
        raise ImportError("pip install google-generativeai")
    genai.configure(api_key=api_key)

    # Convert messages to Gemini format
    history = []
    last_user_msg = ""
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        if msg == messages[-1] and role == "user":
            last_user_msg = msg["content"]
        else:
            history.append({"role": role, "parts": [msg["content"]]})

    gem_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=SYSTEM_PROMPT,
    )
    chat = gem_model.start_chat(history=history)
    resp = chat.send_message(last_user_msg)
    return resp.text


CALLERS = {
    "claude": call_claude,
    "openai": call_openai,
    "grok":   call_grok,
    "gemini": call_gemini,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def print_banner():
    print()
    print(c("bold", "╔══════════════════════════════════════════════════╗"))
    print(c("bold", "║") + c("cyan", "         VIBE CODING ASSISTANT  🤖✨              ") + c("bold", "║"))
    print(c("bold", "║") + c("dim",  "   Claude · OpenAI · Grok · Gemini — all in one  ") + c("bold", "║"))
    print(c("bold", "╚══════════════════════════════════════════════════╝"))
    print()


def print_response(ai_name, text):
    info = AI_INFO[ai_name]
    label = c(info["color"], f"[{info['label']}]")
    print(f"\n{label}")
    # Wrap long lines nicely
    for line in text.split("\n"):
        if len(line) > 100:
            wrapped = textwrap.fill(line, width=100)
            print(wrapped)
        else:
            print(line)
    print()


def pick_ai():
    print(c("bold", "Pick your AI:"))
    keys = list(AI_INFO.keys())
    for i, k in enumerate(keys, 1):
        info = AI_INFO[k]
        key_set = "✅" if os.environ.get(info["env_key"]) else "❌ (no key)"
        print(f"  {c('yellow', str(i))}. {c(info['color'], info['label'])}  {c('dim', key_set)}")
    print(f"  {c('yellow', str(len(keys)+1))}. {c('white', 'Switch mid-chat')}  (type /switch anytime)")
    print()
    while True:
        choice = input(c("cyan", "→ ")).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            return keys[int(choice) - 1]
        # also accept name directly
        if choice.lower() in AI_INFO:
            return choice.lower()
        print(c("red", "  not valid, pick a number"))


def check_key(ai_name):
    info = AI_INFO[ai_name]
    key = os.environ.get(info["env_key"])
    if not key:
        print(c("red", f"\n  ⚠  No API key for {info['label']}"))
        print(c("dim", f"     Add {info['env_key']}=your_key to your .env file\n"))
        return None
    return key


def print_help():
    print(c("dim", textwrap.dedent("""
      Commands:
        /switch    → switch to a different AI
        /clear     → clear conversation history
        /model     → show current model
        /models    → list all default models
        /history   → show message count
        /help      → show this
        /exit      → bye! 👋
        Ctrl+C     → also exits
    """)))


# ── Main chat loop ────────────────────────────────────────────────────────────

def chat_loop(ai_name):
    messages = []  # shared history, carries across /switch

    while True:
        info = AI_INFO[ai_name]
        api_key = check_key(ai_name)
        if not api_key:
            print(c("yellow", "  Switching to a different AI...\n"))
            ai_name = pick_ai()
            continue

        prompt_label = c(info["color"], f"{info['label']} ›")
        print(c("bold", f"\n  Chatting with {c(info['color'], info['label'])}"))
        print(c("dim",  f"  model: {info['model']}  |  /help for commands\n"))

        while True:
            try:
                user_input = input(c("white", "you › ")).strip()
            except (KeyboardInterrupt, EOFError):
                print(c("cyan", "\n\n  Peace out! ✌️\n"))
                sys.exit(0)

            if not user_input:
                continue

            # ── Commands ──────────────────────────────────────────────────────
            if user_input.startswith("/"):
                cmd = user_input.lower().split()[0]

                if cmd == "/exit":
                    print(c("cyan", "\n  Peace out! ✌️\n"))
                    sys.exit(0)

                elif cmd == "/switch":
                    print()
                    ai_name = pick_ai()
                    info = AI_INFO[ai_name]
                    api_key = check_key(ai_name)
                    if not api_key:
                        continue
                    print(c("bold", f"\n  Switched to {c(info['color'], info['label'])}"))
                    print(c("dim",  f"  model: {info['model']}  |  history preserved ({len(messages)} msgs)\n"))
                    continue

                elif cmd == "/clear":
                    messages = []
                    print(c("green", "  History cleared ✓\n"))
                    continue

                elif cmd == "/model":
                    print(c("dim", f"  {info['model']}\n"))
                    continue

                elif cmd == "/models":
                    for k, v in AI_INFO.items():
                        print(c("dim", f"  {k:8s} → {v['model']}"))
                    print()
                    continue

                elif cmd == "/history":
                    print(c("dim", f"  {len(messages)} message(s) in context\n"))
                    continue

                elif cmd == "/help":
                    print_help()
                    continue

                else:
                    print(c("red", f"  Unknown command: {cmd}  (try /help)\n"))
                    continue

            # ── Send to AI ────────────────────────────────────────────────────
            messages.append({"role": "user", "content": user_input})

            print(c("dim", "  thinking..."), end="\r", flush=True)
            try:
                caller = CALLERS[ai_name]
                reply = caller(messages, api_key, info["model"])
                messages.append({"role": "assistant", "content": reply})
                print(" " * 20, end="\r")  # clear "thinking..."
                print_response(ai_name, reply)

            except ImportError as e:
                print(c("red", f"\n  Missing package: {e}\n"))
                messages.pop()  # remove unanswered user msg

            except Exception as e:
                err = str(e)
                print(c("red", f"\n  Error: {err}\n"))
                messages.pop()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vibe Coding Assistant — all AIs, one file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--ai",
        choices=list(AI_INFO.keys()),
        help="Skip the picker and jump straight into an AI",
    )
    args = parser.parse_args()

    print_banner()

    if args.ai:
        ai_name = args.ai
    else:
        ai_name = pick_ai()

    chat_loop(ai_name)


if __name__ == "__main__":
    main()