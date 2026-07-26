# Excalidraw Library

The first Excalidraw collection contains the AI-tool logos from this kit:

- Anthropic
- ChatGPT
- Claude
- Codex
- Gemini
- Grok
- NotebookLM
- OpenAI, GPT, and Sora (one shared mark)
- OpenClaw
- Perplexity
- Poke

## Download And Test

1. Download [`insta360-mic-pro-ai-tools.excalidrawlib`](../downloads/insta360-mic-pro-ai-tools.excalidrawlib).
2. Open Excalidraw.
3. Open the library panel by pressing `9`.
4. Choose **Load library from file** and select the download.
5. Insert several items on light and dark canvases.
6. Confirm each logo inserts as one grouped object and remains transparent.

## Why The Logos Use Native Rectangles

Excalidraw currently prevents image elements from being added to libraries, and
the `.excalidrawlib` format does not include the binary image files used by an
ordinary Excalidraw drawing.

The build script therefore reconstructs each source PNG as merged, native
Excalidraw rectangles. This keeps the library portable, preserves transparent
areas, and makes it eligible for the same publishing path as other public
libraries.

## Rebuild And Validate

```sh
python3 tools/build_excalidraw_library.py
python3 tools/validate_excalidraw_library.py
```

The generated preview is
[`previews/excalidraw-ai-tools-preview.png`](../previews/excalidraw-ai-tools-preview.png).

## Submission Checklist

- Test the downloaded file by loading it into a fresh Excalidraw session.
- Select all 11 library items.
- Choose **Publish** in the Excalidraw library panel.
- Suggested title: `Insta360 Mic Pro — AI Tool Logos`
- Suggested description: `Transparent, Mic Pro-sized logo marks for AI tools, reconstructed as portable native Excalidraw elements.`
- Use the repository URL as the public source.
- Review the generated pull request and respond to maintainer feedback.

The marks remain trademarks and/or copyrighted assets of their respective
owners. See [`TRADEMARKS.md`](../TRADEMARKS.md).
