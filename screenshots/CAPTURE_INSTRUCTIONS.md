# How to Capture the Visualization Screenshot

The automated screenshot capture timed out due to D3.js rendering time. Here's how to manually capture it:

## Quick Method

1. **Open the application** in your browser:
   - Go to http://localhost:5000 (if running locally)
   - Or use your Replit preview URL

2. **Wait for full render** (~5-10 seconds):
   - Let the D3.js force simulation settle
   - Nodes will stop moving when ready

3. **Take screenshot**:
   - **Windows**: Windows Key + Shift + S
   - **Mac**: Cmd + Shift + 4
   - **Linux**: Use Screenshot tool or PrtScn

4. **Save the file**:
   - Save as `visualization.png` in the `screenshots/` directory
   - This will automatically show in the README

## Expected Visualization

Your screenshot should show:
- ✅ **Black background** (cyberpunk theme)
- ✅ **Purple keyword nodes** arranged in outer circle
- ✅ **Image thumbnails** in center area
- ✅ **Green edges** connecting nodes
- ✅ **Radial force-directed layout**

## Alternative: Use Replit's Built-in Screenshot

If you're on Replit:
1. Click the webview tab
2. Use your browser's screenshot tool
3. Crop to show just the visualization
4. Save to `screenshots/visualization.png`

---

Once saved, the image will automatically appear in the README.md file!
