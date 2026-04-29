# Figma MCP Bridge Setup (VS Code)

This guide shows how to set up the Figma MCP bridge so GitHub Copilot in VS Code can read from Figma and write updates back when needed.

## Prerequisites

- VS Code with GitHub Copilot Chat enabled, and the Figma MCP bridge (extension) available in this workspace
- Access to Figma files you want to use
- A Figma account signed into the desktop app or browser

## 1. Confirm Copilot and Figma Access

1. Open VS Code.
2. Open Copilot Chat and verify you are signed in.
3. In Figma, make sure you can open the target file and have edit/view permissions as needed.

## 2. Enable MCP Usage in Chat

1. Open Copilot Chat in VS Code.
2. Start a chat in this workspace.
3. Ask Copilot to read a Figma node with a prompt like:

```text
Use this Figma node and summarize it:
https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>
```

If MCP access is available, Copilot will call Figma tools directly from chat.

## 3. Verify with a Read Test

Use a real Figma URL and request a small read operation first:

```text
Read this Figma node and list its main components and states.
```

Expected result:
- Copilot returns structured node context (layout, layers, states, or generated reference code).

## 4. Verify with a Write Test (Optional)

After read access is working, run a safe write task:

```text
Create a simple test frame in this Figma file named "MCP Bridge Check".
```

Expected result:
- Copilot confirms the action and the frame appears in the target file.

## 5. Recommended Prompt Pattern

When working from design to code, include both URL and intent:

```text
Implement this component from Figma in Vue.
URL: https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>
Requirements: pure SVG, semantic tokens only, typed props, etc, as described in the authoring workflow document.
```

## Troubleshooting

### Copilot cannot access Figma

- Re-authenticate your GitHub Copilot session in VS Code.
- Ensure your Figma account still has access to the file.
- Retry with a direct node URL (including `node-id`).

### Link opens but node data is missing

- Make sure the URL is a `figma.com/design/...` link.
- Ensure `node-id` is present and points to an existing node.
- Try a smaller node/frame first.

### Writes fail

- Confirm edit permissions on the Figma file.
- Try a minimal write action first (new frame, text node, or color update).
- If your organization restricts integrations, ask your admin to allow Figma MCP usage.

## Security Notes

- Do not paste secrets/tokens in chat prompts.
- Prefer links to specific nodes instead of sharing entire design files when possible.
- Use least-privilege access for team files.

## Next Steps

- Use [Mimic Component Authoring Workflow](/mimics/authoring-workflow) for component implementation.
- Use [Mimic Components Overview](/mimics/) for available mimic primitives.
