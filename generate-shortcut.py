#!/usr/bin/env python3
"""Generate an Apple Shortcut (.shortcut) file for the Prompt Generator."""
import plistlib
import sys
import json

def make_text_token(s):
    return {
        "Value": {"string": s, "attachmentsByRange": {}},
        "WFSerializationType": "WFTextTokenString"
    }

def make_var_token(name):
    return {
        "Value": {"Type": "Variable", "VariableName": name},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def make_magic_var(action_uuid, output_name=""):
    d = {"Type": "ActionOutput", "OutputUUID": action_uuid}
    if output_name:
        d["OutputName"] = output_name
    return {"Value": d, "WFSerializationType": "WFTextTokenAttachment"}

api_key = sys.argv[1] if len(sys.argv) > 1 else "YOUR_API_KEY"

system_prompt = """You are the world's most advanced Claude Code Prompt Architect. Your ONLY job is to transform a user's raw, unfiltered idea — however messy, spoken, or incomplete — into a perfectly engineered, zero-failure Claude Code prompt.

You operate at hyper-human reasoning level. You do not take inputs literally — you understand *intent*. You read between the lines. You fill structural gaps. You anticipate what the user actually wants built and what Claude Code will need to know to build it without errors, ambiguity, or hallucination.

You understand that Claude 4.x takes instructions *literally*. It does not infer. It does not guess. It does not expand vague requests. Therefore your output must be explicit, complete, and leave nothing to interpretation.

EVERY prompt you generate must follow this exact structure (use these exact XML-style headers in your output):

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
10. The prompt you produce must be good enough that Claude Code can execute it in one pass, without needing to ask clarifying questions."""

body_json = json.dumps({
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 8000,
    "system": system_prompt,
    "messages": [{"role": "user", "content": "IDEA_PLACEHOLDER"}]
})

shortcut = {
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4274264319,
        "WFWorkflowIconGlyphNumber": 61440
    },
    "WFWorkflowClientVersion": "2612.0.4",
    "WFWorkflowOutputContentItemClasses": ["WFStringContentItem"],
    "WFWorkflowHasOutputFallback": False,
    "WFWorkflowName": "Prompt Generator",
    "WFWorkflowImportQuestions": [],
    "WFWorkflowTypes": [],
    "WFQuickActionSurfaces": [],
    "WFWorkflowHasShortcutInputVariables": False,
    "WFWorkflowActions": [
        # 1. Ask for input (supports dictation)
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
            "WFWorkflowActionParameters": {
                "WFAskActionPrompt": "What do you want to build?",
                "WFAskActionDefaultAnswer": "",
                "WFInputType": "Text"
            }
        },
        # 2. Store user input
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
            "WFWorkflowActionParameters": {
                "WFVariableName": "userIdea"
            }
        },
        # 3. Build the request body text
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
            "WFWorkflowActionParameters": {
                "WFTextActionText": make_text_token(body_json)
            }
        },
        # 4. Store body template
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
            "WFWorkflowActionParameters": {
                "WFVariableName": "bodyTemplate"
            }
        },
        # 5. Replace placeholder with actual user input
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.text.replace",
            "WFWorkflowActionParameters": {
                "WFInput": make_var_token("bodyTemplate"),
                "WFReplaceTextFind": "IDEA_PLACEHOLDER",
                "WFReplaceTextReplace": make_var_token("userIdea")
            }
        },
        # 6. Store final body
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
            "WFWorkflowActionParameters": {
                "WFVariableName": "requestBody"
            }
        },
        # 7. Show "Generating..." notification
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
            "WFWorkflowActionParameters": {
                "WFNotificationActionBody": "Generating your perfect prompt...",
                "WFNotificationActionTitle": "Prompt Generator"
            }
        },
        # 8. API call
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
            "WFWorkflowActionParameters": {
                "WFURL": "https://api.anthropic.com/v1/messages",
                "WFHTTPMethod": "POST",
                "WFHTTPHeaders": {
                    "Value": {
                        "WFDictionaryFieldValueItems": [
                            {
                                "WFItemType": 0,
                                "WFKey": make_text_token("x-api-key"),
                                "WFValue": make_text_token(api_key)
                            },
                            {
                                "WFItemType": 0,
                                "WFKey": make_text_token("anthropic-version"),
                                "WFValue": make_text_token("2023-06-01")
                            },
                            {
                                "WFItemType": 0,
                                "WFKey": make_text_token("content-type"),
                                "WFValue": make_text_token("application/json")
                            }
                        ]
                    },
                    "WFSerializationType": "WFDictionaryFieldValue"
                },
                "WFHTTPBodyType": "String",
                "WFHTTPTextBody": make_var_token("requestBody")
            }
        },
        # 9. Store API response
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
            "WFWorkflowActionParameters": {
                "WFVariableName": "apiResponse"
            }
        },
        # 10. Get "content" key from response
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "WFInput": make_var_token("apiResponse"),
                "WFDictionaryKey": "content"
            }
        },
        # 11. Get first item from content array
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getitemfromlist",
            "WFWorkflowActionParameters": {
                "WFItemSpecifier": "First Item"
            }
        },
        # 12. Get "text" from first content item
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "WFDictionaryKey": "text"
            }
        },
        # 13. Store generated prompt
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
            "WFWorkflowActionParameters": {
                "WFVariableName": "generatedPrompt"
            }
        },
        # 14. Copy to clipboard
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setclipboard",
            "WFWorkflowActionParameters": {
                "WFInput": make_var_token("generatedPrompt")
            }
        },
        # 15. Show the result
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.alert",
            "WFWorkflowActionParameters": {
                "WFAlertActionMessage": make_var_token("generatedPrompt"),
                "WFAlertActionTitle": "Your Prompt (copied to clipboard)",
                "WFAlertActionCancelButtonShown": False
            }
        }
    ]
}

output_path = "/home/user/olivia-landing/PromptGenerator.shortcut"
with open(output_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

print(f"Shortcut written to {output_path}")
