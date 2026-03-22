# THE PERFECT PROMPT GENERATOR — BUILD PROMPT

## ROLE

You are a senior full-stack engineer and UI craftsman. Build a production-grade, single-file desktop web application called the **Perfect Prompt Generator** — a tool that transforms a user's raw idea (typed or spoken) into a flawless, perfectly-structured Claude Code prompt, every single time.

---

## CONTEXT

This is a standalone developer tool. It is not part of any existing product or brand. It exists to solve one problem: turning messy human ideas into executable Claude Code prompts that work on the first pass with zero follow-up questions. The user will open this file locally on their computer in Chrome, Firefox, or Safari.

---

## TASK

Build a single `index.html` file — a dark, premium-looking desktop app where the user can:

1. **Paste their Anthropic API key** into a secure input field (with show/hide toggle)
2. **Type** their raw idea into a large textarea — OR —
3. **Speak** their idea using their microphone (Web Speech API)
4. Hit **Generate** and watch the response **stream in token-by-token** in real time
5. **Copy** the generated prompt to clipboard with one click
6. **Cancel** a generation in progress

The AI brain that transforms input into the perfect prompt is powered by a call to the **Anthropic Messages API** (`https://api.anthropic.com/v1/messages`) using model `claude-sonnet-4-20250514` with `max_tokens: 8000` and streaming enabled.

---

## TECHNICAL REQUIREMENTS

### Stack
- Single HTML file — no build tools, no frameworks, no npm
- Vanilla JS + CSS only
- Google Fonts loaded via CDN: `Syne` (headings), `JetBrains Mono` (code output), `Inter` (body/UI)
- Anthropic API called directly from browser using `fetch()` with streaming (`stream: true`)

### API Call Specifications
- Endpoint: `https://api.anthropic.com/v1/messages`
- Method: POST
- Headers:
  - `Content-Type: application/json`
  - `anthropic-version: 2023-06-01`
  - `anthropic-dangerous-direct-browser-access: true`
  - `x-api-key: [user's key from input field]`
- Body: `{ model: "claude-sonnet-4-20250514", max_tokens: 8000, stream: true, system: BRAIN_SYSTEM_PROMPT, messages: [{ role: "user", content: userInput }] }`
- Streaming: Read response via `response.body.getReader()`, parse SSE lines, handle event types: `content_block_delta` (append `delta.text`), `message_stop` (done), `ping` (ignore)
- Timeout: 60-second `AbortController` timeout on the fetch
- The user provides their own API key — do NOT hardcode one

### API Key Handling
- Input field at top of the page, `type="password"` by default
- Small eye icon toggle button to show/hide the key
- Validate format starts with `sk-ant-` before allowing generation
- Show inline error if key is missing or malformed

### Voice Input
- Use `window.SpeechRecognition || window.webkitSpeechRecognition`
- `continuous: true`, `interimResults: true`, `lang: 'en-US'`
- Transcription appears live in textarea as user speaks
- Visual pulse animation on mic button while listening
- Toggle on/off with same button
- If browser doesn't support it: hide mic button entirely, no errors
- Clean up recognition instances after use

### Streaming Output
- As tokens arrive, append them to the output panel in real time — the user sees text appearing word by word
- Use a blinking cursor character `|` at the end of the streaming text that disappears when complete
- Show token count and elapsed time below the output when generation is done (e.g., "2,847 tokens in 12.3s")

### Cancel / Abort
- While generating, the Generate button changes to a "Stop" button (red accent)
- Clicking Stop calls `controller.abort()` on the fetch and stops streaming
- Output panel keeps whatever text was received so far

---

## DESIGN SPECIFICATIONS

### Color System
```
--bg:           #0a0a0f          (page background)
--bg2:          #0d0d1a          (card backgrounds)
--surface:      rgba(255,255,255,0.04)  (glass panels)
--border:       rgba(255,255,255,0.07)  (subtle borders)
--border-hover: rgba(201,168,76,0.45)   (hover borders)
--gold:         #C9A84C          (primary accent — buttons, highlights)
--gold-dim:     #8a6f2f          (muted gold)
--gold-glow:    rgba(201,168,76,0.25)   (glow/shadow effects)
--indigo:       #6366f1          (secondary accent — gradient partner)
--white:        #f0f0f8          (primary text)
--gray:         #8888aa          (secondary text, placeholders)
--error:        #ef4444          (error states)
--success:      #22c55e          (success states like "Copied!")
```

### Typography
- **Headings**: `Syne`, weight 700-800
- **Body/UI**: `Inter`, weight 400-500
- **Code output**: `JetBrains Mono`, weight 400, size 0.85rem, line-height 1.7
- **API key input**: `JetBrains Mono`, size 0.82rem

### Layout
- Max-width: 880px, centered
- Two-panel vertical layout: Input card on top, Output card below
- Generous padding: 2rem page, 1.5rem cards
- All cards use glassmorphism: `backdrop-filter: blur(12px)`, surface background, subtle border

### Particle Background
- Full-viewport `<canvas>` behind everything, fixed position, `pointer-events: none`, opacity 0.5
- 120 particles: 60% gold `rgb(201,168,76)`, 40% blue `rgb(76,139,201)`
- Radius: 0.3-1.8px, random alpha 0.1-0.7
- Velocity: random ±0.2 on x/y, bounce at edges
- Draw connecting lines between particles within 110px distance
- Line opacity: `0.08 * (1 - distance/110)`

### Animations
- **Page load**: Fade in body over 0.6s
- **Breathe**: Hero title text-shadow pulses between `0 0 30px #C9A84C66` and `0 0 55px #C9A84Caa` over 4s, infinite
- **Mic pulse**: When listening, mic button box-shadow pulses `0 0 0 0` to `0 0 0 12px transparent` over 1.5s
- **Output slide-in**: Output panel slides up from `translateY(20px)` with `opacity: 0` to visible, 0.5s ease
- **Gradient border**: When output has content, animated gradient border (gold → indigo → gold) using `::before` pseudo-element with mask-composite, background-size 200%, animating position over 4s
- **Loading dots**: Three dots pulsing opacity/scale with staggered delays (0, 0.2s, 0.4s)
- **Streaming cursor**: Blinking `|` character, opacity toggling 0→1 every 0.6s
- **Button hover**: `translateY(-2px)` lift + gold glow shadow, 0.2s transition
- **Card hover**: Border color transitions to `--border-hover`, 0.3s

### Visual States (all must be visually distinct)
1. **Idle**: Empty output area, generate button disabled (0.35 opacity), neutral borders
2. **Listening**: Mic button has gold border + pulse animation, subtle gold glow on textarea border
3. **Generating**: Generate button becomes red "Stop" button, output panel visible with streaming text + blinking cursor, loading dots if no text yet
4. **Complete**: Output has full text, animated gradient border on output card, Copy button visible, token/time stats shown
5. **Error**: Output card has red border, red `::before` gradient, error icon (SVG !) + error message in red, no copy button

### Scrollbar Styling
```css
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #8a6f2f; border-radius: 3px; }
scrollbar-width: thin;
scrollbar-color: #8a6f2f transparent;
```

---

## BRAIN SYSTEM PROMPT

Store this as `const BRAIN_SYSTEM_PROMPT` — a template literal. This is the exact system parameter sent in every API call:

```
You are the world's most advanced Claude Code Prompt Architect. Your ONLY job is to transform a user's raw, unfiltered idea — however messy, spoken, or incomplete — into a perfectly engineered, zero-failure Claude Code prompt.

You operate at hyper-human reasoning level. You do not take inputs literally — you understand *intent*. You read between the lines. You fill structural gaps. You anticipate what the user actually wants built and what Claude Code will need to know to build it without errors, ambiguity, or hallucination.

You understand that Claude 4.x takes instructions *literally*. It does not infer. It does not guess. It does not expand vague requests. Therefore your output must be explicit, complete, and leave nothing to interpretation.

EVERY prompt you generate must follow this exact structure (use these exact headers in your output):

---

## ROLE
[One sentence. Who Claude Code is for this task. Make it specific to the domain being built.]

## CONTEXT
[2-4 sentences. What project/product/system this fits into. What already exists. What the user's goals are. Why this matters. What NOT to do or build beyond scope.]

## TASK
[The core build instruction. Be specific about what to create. Use concrete nouns — not vague verbs. Include filenames, tech stack, and architecture decisions where relevant. If it's a UI, describe the exact components. If it's an API, describe the endpoints. If it's a script, describe the inputs/outputs.]

## TECHNICAL REQUIREMENTS
[Bullet list. Every tech constraint: language, framework, libraries, file structure, environment. If the user didn't specify, make smart inferences based on what they're building. Include version preferences where relevant.]

## ACCEPTANCE CRITERIA
[Bullet list. This is the definition of done. Each item must be binary — either it's done or it isn't. No vague items like "works well." Each criterion must be testable. E.g. "User can click X and Y happens" or "API returns Z when given input W."]

## OUTPUT FORMAT
[Describe exactly how Claude Code should deliver its output: which files to create, what the file structure should look like, whether to write to disk, whether to show a summary after finishing. Be explicit.]

## CONSTRAINTS & EDGE CASES
[Bullet list. What Claude Code must NOT do. Common failure modes to avoid. Security considerations. Things to handle gracefully. Explicit scope limits.]

## SUCCESS SIGNAL
[One sentence. How the user will know the task is completely done and working correctly.]

---

RULES YOU MUST FOLLOW:

1. NEVER produce a vague prompt. If the user gave you a vague idea, you make it specific. That is your job.
2. ALWAYS fill in what the user didn't say if it's needed to make the prompt complete and executable.
3. NEVER add unnecessary complexity. Only include what the build actually requires.
4. ALWAYS explain WHY constraints exist, not just state them — Claude Code follows motivated instructions better.
5. ALWAYS write Acceptance Criteria as binary, testable conditions.
6. NEVER use filler phrases like "comprehensive," "robust," or "user-friendly" without defining what those mean concretely.
7. If the user's idea is for a UI, always specify visual behavior, states, and interactions explicitly.
8. If the user's idea involves AI or APIs, always specify the model, the call structure, error handling, and expected response format.
9. Output ONLY the generated prompt — no preamble, no explanation, no meta-commentary. Just the finished, ready-to-paste Claude Code prompt.
10. The prompt you produce must be good enough that Claude Code can execute it in one pass, without needing to ask clarifying questions.
```

---

## ACCEPTANCE CRITERIA

- [ ] Single `index.html` file — opens directly in a browser, no server needed
- [ ] API key input at top with show/hide toggle; validates `sk-ant-` prefix
- [ ] User can type a raw idea into the textarea and click Generate
- [ ] User can click the mic button, speak, and see live transcription in the textarea
- [ ] Mic button shows gold pulse animation while listening, stops on second click or speech end
- [ ] Mic button is hidden (not broken) in browsers without SpeechRecognition support
- [ ] Generate button is disabled when textarea is empty or when API key is missing
- [ ] Clicking Generate with `stream: true` shows tokens appearing in real time in the output panel
- [ ] A blinking cursor `|` appears at the end of streaming text and disappears when done
- [ ] Token count and elapsed time are displayed below output after generation completes
- [ ] Generate button becomes a red "Stop" button during generation; clicking it aborts the request
- [ ] Stopped generation keeps partial output visible
- [ ] Fetch has a 60-second AbortController timeout
- [ ] Specific error messages for: 401 (bad key), 429 (rate limit), 400 (bad request), network errors, timeout
- [ ] Copy button copies output to clipboard, shows "Copied!" in green for 2 seconds
- [ ] Character count updates in real time below the textarea
- [ ] Particle canvas background with gold/blue particles and connecting lines
- [ ] Hero title has breathing text-shadow animation
- [ ] Output panel slides in from below on first appearance
- [ ] Output card has animated gradient border (gold/indigo) when content is present
- [ ] Error state shows red border, red gradient, error icon
- [ ] All 5 visual states (idle, listening, generating, complete, error) are distinct
- [ ] Dark theme matches specified color system exactly
- [ ] Works on Chrome, Firefox, Safari desktop — no build step

---

## OUTPUT FORMAT

Write one file to disk:
```
index.html
```
All CSS in a `<style>` tag in `<head>`. All JavaScript in a `<script>` tag at the bottom of `<body>`. No external JS files. No module imports. Everything self-contained.

After writing, confirm the file path and summarize: key features implemented, the 5 visual states, and how to use it.

---

## CONSTRAINTS & EDGE CASES

- Do NOT use React, Vue, Svelte, or any JS framework — vanilla JS only
- Do NOT use localStorage, sessionStorage, or cookies
- Do NOT hardcode any API key — the user provides their own
- Do NOT make the UI feel like a ChatGPT clone — this must feel like a premium proprietary tool
- Handle the case where `SpeechRecognition` is not supported: hide the mic button entirely, no console errors
- Do NOT send the API call if textarea is empty — show inline warning
- Do NOT send the API call if API key is empty or doesn't start with `sk-ant-` — show inline error
- If the API returns a non-200 status, parse the error JSON and display a human-readable message with specific guidance (e.g., "Invalid API key" for 401, "Rate limited — wait a moment" for 429)
- If the network request times out (60s), show "Request timed out. Please try again."
- If `response.body.getReader()` fails (unlikely), fall back to non-streaming `response.json()` and display the full result at once
- Clean up speech recognition instances after use to prevent memory leaks
- The streaming parser must handle partial SSE chunks (data split across reads) — buffer incomplete lines
- Escape any HTML in error messages to prevent XSS

---

## SUCCESS SIGNAL

The app is done when you can open `index.html` in Chrome, paste an API key, type any rough idea, click Generate, watch the response stream in token-by-token with a blinking cursor, see the final prompt with an animated gold-indigo border, copy it to clipboard, and paste it into Claude Code — and it executes perfectly on the first pass.
