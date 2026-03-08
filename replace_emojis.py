import os
import glob
import re

# Simple SVG definitions matching the requested aesthetics.
# Using standard 24x24 viewBox stroke icons
def svg(path_d):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; display: inline-block;">{path_d}</svg>'

icons = {
    '✅': svg('<polyline points="20 6 9 17 4 12"></polyline>'),
    '✓': svg('<polyline points="20 6 9 17 4 12"></polyline>'),
    '❌': svg('<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'),
    '✗': svg('<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'),
    '🔴': svg('<circle cx="12" cy="12" r="10" fill="currentColor" stroke="none"></circle>'),
    '🟢': svg('<circle cx="12" cy="12" r="10" fill="currentColor" stroke="none"></circle>'),
    '⚠️': svg('<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>'),
    '🚪': svg('<path d="M18 20V5a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v15"></path><path d="M2 20h20"></path><path d="M14 12v.01"></path>'),
    '🍽️': svg('<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"></path><path d="M7 2v20"></path><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"></path>'),
    '🎫': svg('<rect x="2" y="7" width="20" height="10" rx="2" ry="2"></rect><path d="M7 7v10"></path><path d="M17 7v10"></path>'),
    '🛡️': svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>'),
    '👤': svg('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>'),
    '👥': svg('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>'),
    '📷': svg('<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle>'),
    '🎥': svg('<polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>'),
    '📲': svg('<rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line>'),
    '⚡': svg('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'),
    '🔄': svg('<polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>'),
    '🙋': svg('<path d="M18 20V10"></path><path d="M12 20V4"></path><path d="M6 20v-4"></path>'),
    '🕐': svg('<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>'),
    '⏱': svg('<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>'),
    '⏳': svg('<path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>'),
    '📢': svg('<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>'),
    '🔍': svg('<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>'),
    '📥': svg('<polyline points="8 17 12 21 16 17"></polyline><line x1="12" y1="12" x2="12" y2="21"></line><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"></path>'),
    '✏️': svg('<path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>'),
    '🗑️': svg('<polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2-2v2"></path>'),
    '⬇': svg('<line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline>'),
    '📅': svg('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>'),
    '📍': svg('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle>'),
    '🏅': svg('<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>'),
    '🏆': svg('<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"></path>'),
    '💬': svg('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>'),
    '✦': svg('<polygon points="12 2 15 9 22 12 15 15 12 22 9 15 2 12 9 9 12 2"></polygon>'),
    '🔥': svg('<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path>'),
    '⭐': svg('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>'),
    '💡': svg('<path d="M9 18h6"></path><path d="M10 22h4"></path><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"></path>'),
    '🥇': svg('<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline><text x="12" y="11" font-size="6" text-anchor="middle" font-family="sans-serif" fill="currentColor" stroke="none">1</text>'),
    '🥈': svg('<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline><text x="12" y="11" font-size="6" text-anchor="middle" font-family="sans-serif" fill="currentColor" stroke="none">2</text>'),
    '🥉': svg('<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline><text x="12" y="11" font-size="6" text-anchor="middle" font-family="sans-serif" fill="currentColor" stroke="none">3</text>'),
}

base_dir = r"c:\SAM\Projects\pre final (8.03.26)\08-03\tamil\templates"

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".html"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()
            
            modified = False
            for emoji, svg_str in icons.items():
                if emoji in content:
                    content = content.replace(emoji, svg_str)
                    modified = True
            
            if modified:
                with open(fpath, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"Updated {fpath}")

print("Emoji replacement complete.")
