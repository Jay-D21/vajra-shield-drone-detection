import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

output_dir = r"c:\Users\ADMIN\Downloads\Drone Detection\report_assets"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------------------
# FIGURE 1: VAJRA-SHIELD SYSTEM ARCHITECTURE PIPELINE
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
ax.set_facecolor("#0F172A") # Slate 900
fig.patch.set_facecolor("#0F172A")

# Title
ax.text(0.5, 0.94, "VAJRA-SHIELD: HIGH-THROUGHPUT DRONE DETECTION ARCHITECTURE",
        ha="center", va="center", color="#F8FAFC", fontsize=16, fontweight="bold", family="sans-serif")
ax.text(0.5, 0.88, "End-to-End Real-Time Aerial Threat Detection & Classification Pipeline",
        ha="center", va="center", color="#94A3B8", fontsize=11, family="sans-serif")

# Define stages
stages = [
    {
        "title": "Stage 1: Multi-Source Ingestion",
        "color": "#3B82F6", # Blue
        "box": (0.04, 0.45, 0.18, 0.35),
        "items": ["• Live RTSP / Webcam (0)", "• HD Video Streams (.mp4)", "• Still Surveillance Frames", "• 30+ FPS Frame Buffer"]
    },
    {
        "title": "Stage 2: Vision Preprocessing",
        "color": "#06B6D4", # Cyan
        "box": (0.27, 0.45, 0.18, 0.35),
        "items": ["• Adaptive Resize (640x640)", "• Letterbox Padding", "• HSV Color Normalization", "• Tensor Conversion (FP32/FP16)"]
    },
    {
        "title": "Stage 3: Deep Feature Core",
        "color": "#8B5CF6", # Purple
        "box": (0.50, 0.45, 0.22, 0.35),
        "items": ["• YOLOv8 CSPDarknet Backbone", "• C2f Multi-Scale Extractors", "• PAN-FPN Bidirectional Neck", "• Anchor-Free Decoupled Heads"]
    },
    {
        "title": "Stage 4: Inference & HUD Alert",
        "color": "#EF4444", # Red
        "box": (0.77, 0.45, 0.19, 0.35),
        "items": ["• IoU NMS (Threshold = 0.45)", "• Conf Filtering (Thresh = 0.35)", "• Target Class Split (Bird vs Drone)", "• Real-Time Threat Banner & HUD"]
    }
]

for stage in stages:
    x, y, w, h = stage["box"]
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor="#1E293B", edgecolor=stage["color"], linewidth=2.2)
    ax.add_patch(rect)
    
    # Header box
    hdr = patches.FancyBboxPatch((x, y + h - 0.08), w, 0.08, boxstyle="round,pad=0.01,rounding_size=0.02",
                                facecolor=stage["color"], edgecolor="none")
    ax.add_patch(hdr)
    ax.text(x + w/2, y + h - 0.04, stage["title"], ha="center", va="center",
            color="#FFFFFF", fontsize=9.5, fontweight="bold")
    
    # Text items
    for idx, item in enumerate(stage["items"]):
        ax.text(x + 0.02, y + h - 0.13 - (idx * 0.055), item, ha="left", va="center",
                color="#E2E8F0", fontsize=8.5)

# Connectors (Arrows)
arrows = [(0.22, 0.62, 0.27, 0.62), (0.45, 0.62, 0.50, 0.62), (0.72, 0.62, 0.77, 0.62)]
for x1, y1, x2, y2 in arrows:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                                color="#38BDF8", lw=2.5))

# Bottom Output Channels Box
out_rect = patches.FancyBboxPatch((0.15, 0.08), 0.70, 0.24, boxstyle="round,pad=0.02,rounding_size=0.03",
                                  facecolor="#1E293B", edgecolor="#10B981", linewidth=2.0)
ax.add_patch(out_rect)
ax.text(0.5, 0.26, "OPERATIONAL OUTPUTS & THREAT INTERFACE", ha="center", va="center",
        color="#34D399", fontsize=11, fontweight="bold")

outputs = [
    ("[ALERT] Red Threat Banner", "Real-time bottom banner on drone detection with count and location"),
    ("[SAFE] Avian HUD Tagging", "Avian classification (Bird) suppressing false-positive alarms"),
    ("[STATS] Telemetry Overlay", "Live FPS counter, target counts, frame statistics overlay"),
    ("[ARCHIVE] Forensic Recording", "High-efficiency XVID/MP4 video storage for incident auditing")
]

for idx, (title, desc) in enumerate(outputs):
    ox = 0.18 + (idx % 2) * 0.35
    oy = 0.18 - (idx // 2) * 0.075
    ax.text(ox, oy, title, color="#F8FAFC", fontsize=9, fontweight="bold")
    ax.text(ox, oy - 0.032, desc, color="#94A3B8", fontsize=7.5)

# Arrow from Stage 4 to Outputs
ax.annotate("", xy=(0.70, 0.32), xytext=(0.86, 0.45),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                            color="#10B981", lw=2.2, connectionstyle="arc3,rad=-0.2"))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
plt.tight_layout()
arch_path = os.path.join(output_dir, "fig1_system_architecture.png")
plt.savefig(arch_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
plt.close()
print("Generated:", arch_path)

# -------------------------------------------------------------------------
# FIGURE 2 & FIGURE 8: SYNTHETIC TEST FRAMES WITH HUD AND THREAT BANNER
# -------------------------------------------------------------------------
def create_hud_frame(bg_color=(35, 45, 60), objects=None, alert=False, alert_text="", frame_idx=142):
    w, h = 960, 540
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw sky gradient or subtle grid
    for y in range(h):
        r = int(bg_color[0] + (y / h) * 35)
        g = int(bg_color[1] + (y / h) * 40)
        b = int(bg_color[2] + (y / h) * 45)
        draw.line([(0, y), (w, y)], fill=(min(255, r), min(255, g), min(255, b)))
    
    # Draw cloud-like or skyline shapes
    draw.polygon([(0, 480), (180, 440), (380, 470), (600, 430), (820, 460), (960, 450), (960, 540), (0, 540)], fill=(20, 30, 42))
    
    # HUD top left
    draw.text((15, 18), f"VAJRA-SHIELD | Frame {frame_idx}", fill=(0, 255, 0))
    d_count = sum(1 for obj in objects if obj["class"] == "drone") if objects else 0
    b_count = sum(1 for obj in objects if obj["class"] == "bird") if objects else 0
    draw.text((15, 45), f"Drones: {d_count} | Birds: {b_count}", fill=(255, 200, 0))
    
    # Draw detected objects
    if objects:
        for obj in objects:
            box = obj["box"]
            cls = obj["class"]
            conf = obj["conf"]
            color = (255, 0, 0) if cls == "drone" else (0, 220, 0)
            
            # Draw box with thickness 3
            draw.rectangle(box, outline=color, width=3)
            
            # Label banner
            label = f"DRONE {conf:.0%}" if cls == "drone" else f"BIRD {conf:.0%}"
            draw.rectangle([(box[0], max(0, box[1] - 22)), (box[0] + 110, box[1])], fill=color)
            draw.text((box[0] + 6, max(2, box[1] - 18)), label, fill=(255, 255, 255))
            
            # Simple drone or bird silhouette inside box
            cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
            if cls == "drone":
                # Quadcopter shape
                draw.ellipse([(cx-25, cy-8), (cx+25, cy+8)], fill=(15, 20, 25))
                draw.line([(cx-28, cy-12), (cx+28, cy+12)], fill=(40, 40, 40), width=3)
                draw.line([(cx-28, cy+12), (cx+28, cy-12)], fill=(40, 40, 40), width=3)
                draw.ellipse([(cx-34, cy-16), (cx-22, cy-8)], outline=(180, 0, 0), width=2)
                draw.ellipse([(cx+22, cy-16), (cx+34, cy-8)], outline=(180, 0, 0), width=2)
                draw.ellipse([(cx-34, cy+8), (cx-22, cy+16)], outline=(180, 0, 0), width=2)
                draw.ellipse([(cx+22, cy+8), (cx+34, cy+16)], outline=(180, 0, 0), width=2)
            else:
                # Bird shape (wings)
                draw.arc([(cx-30, cy-15), (cx, cy+10)], start=180, end=360, fill=(20, 20, 20), width=3)
                draw.arc([(cx, cy-15), (cx+30, cy+10)], start=180, end=360, fill=(20, 20, 20), width=3)

    # Bottom Alert Banner
    if alert:
        draw.rectangle([(0, h - 50), (w, h)], fill=(200, 0, 0))
        draw.text((w // 2 - 180, h - 34), alert_text, fill=(255, 255, 255))
        
    return img

# Figure 2: Drone Detected Threat
drone_img = create_hud_frame(
    objects=[{"box": [480, 160, 640, 290], "class": "drone", "conf": 0.94}],
    alert=True,
    alert_text="!! THREAT: 1 DRONE(S) DETECTED !!",
    frame_idx=184
)
drone_path = os.path.join(output_dir, "fig2_drone_detection_hud.png")
drone_img.save(drone_path)
print("Generated:", drone_path)

# Figure 8: Bird Non-Threat Safe Discrimination
bird_img = create_hud_frame(
    objects=[
        {"box": [220, 140, 340, 230], "class": "bird", "conf": 0.92},
        {"box": [560, 100, 660, 180], "class": "bird", "conf": 0.88}
    ],
    alert=False,
    alert_text="",
    frame_idx=215
)
bird_path = os.path.join(output_dir, "fig8_bird_discrimination.png")
bird_img.save(bird_path)
print("Generated:", bird_path)
