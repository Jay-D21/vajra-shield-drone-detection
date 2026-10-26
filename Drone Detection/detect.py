# ============================================================
# VAJRA-SHIELD — DETECT DRONES IN IMAGE / VIDEO / WEBCAM
# ============================================================
# Usage:
#   python detect.py --source image.jpg
#   python detect.py --source video.mp4
#   python detect.py --source 0              (webcam live)
#   python detect.py --source folder/        (all images in folder)
#
# Optional:
#   --conf 0.4       confidence threshold (default 0.35)
#   --model path.pt  custom model (default: runs/vajra_v1/weights/best.pt)
#   --save-video      save annotated video to output/
# ============================================================

import argparse
import os
import sys
import cv2
from ultralytics import YOLO

CLASS_NAMES = ["bird", "drone"]
COLORS = {
    "bird":  (0, 200, 0),    # Green — non-threat
    "drone": (0, 0, 255),    # Red   — THREAT
}


def find_model():
    """Auto-find the best.pt model from training runs."""
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, "runs", "vajra_v1", "weights", "best.pt"),
        os.path.join(base, "runs", "vajra_drone_v1", "weights", "best.pt"),
        os.path.join(base, "best.pt"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def detect_image(model, source, conf):
    """Run detection on a single image and display it."""
    results = model.predict(source=source, conf=conf, iou=0.45, verbose=False)

    for r in results:
        print(f"\n  Detected {len(r.boxes)} object(s) in: {source}")
        for box in r.boxes:
            cls_id = int(box.cls[0])
            c = float(box.conf[0])
            name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else "?"
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            tag = "🚨 DRONE" if name == "drone" else "   bird "
            print(f"    {tag}  conf={c:.0%}  box=[{x1},{y1},{x2},{y2}]")

        # Show image
        frame = r.plot(line_width=2)
        cv2.imshow("Vajra-Shield Detection", frame)
        print("\n  Press any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def detect_video(model, source, conf, save_output=False):
    """Run detection on video or webcam with live display."""
    # Webcam if source is a number
    is_webcam = False
    try:
        source = int(source)
        is_webcam = True
    except ValueError:
        pass

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"  ❌ Cannot open: {source}")
        return

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if not is_webcam else 0

    src_name = "Webcam" if is_webcam else os.path.basename(str(source))
    print(f"  Source     : {src_name}")
    print(f"  Resolution : {width}x{height} @ {fps} FPS")
    if total > 0:
        print(f"  Duration   : {total/fps:.1f}s ({total} frames)")
    print(f"  Press 'A' to stop\n")

    # Video writer for saving
    writer = None
    if save_output and not is_webcam:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"detected_{src_name}")
        if not out_path.lower().endswith(".avi"):
            out_path = os.path.splitext(out_path)[0] + ".avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
        print(f"  Saving to: {out_path}\n")

    frame_num = 0
    drone_total = 0
    bird_total = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_num += 1

        # Detect
        results = model.predict(source=frame, conf=conf, iou=0.45, verbose=False)

        for r in results:
            annotated = r.plot(line_width=2)

            # Count detections
            drones_now = 0
            for box in r.boxes:
                cls_id = int(box.cls[0])
                if cls_id == 1:
                    drone_total += 1
                    drones_now += 1
                elif cls_id == 0:
                    bird_total += 1

            # HUD overlay
            cv2.putText(annotated, f"VAJRA-SHIELD | Frame {frame_num}",
                        (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated, f"Drones: {drone_total} | Birds: {bird_total}",
                        (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

            # Alert banner when drone found
            if drones_now > 0:
                cv2.rectangle(annotated, (0, height - 45), (width, height), (0, 0, 200), -1)
                text = f"!! THREAT: {drones_now} DRONE(S) DETECTED !!"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                tx = (width - text_size[0]) // 2
                cv2.putText(annotated, text, (tx, height - 14),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Vajra-Shield — Drone Detection", annotated)

            if writer:
                writer.write(annotated)

        # Quit on Q
        if cv2.waitKey(1) & 0xFF == ord("a"):
            print("  Stopped by user.")
            break

        # Progress (video only)
        if not is_webcam and frame_num % 100 == 0:
            pct = frame_num / total * 100 if total else 0
            print(f"  Frame {frame_num}/{total} ({pct:.0f}%) "
                  f"| Drones: {drone_total} | Birds: {bird_total}")

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()

    print(f"\n  {'='*45}")
    print(f"  Done — {frame_num} frames processed")
    print(f"  Total drone detections : {drone_total}")
    print(f"  Total bird detections  : {bird_total}")
    if writer:
        print(f"  Output saved to        : {out_path}")
    print(f"  {'='*45}")


def main():
    parser = argparse.ArgumentParser(description="Vajra-Shield Drone Detection")
    parser.add_argument("--source", required=True,
                        help="Image, video file, folder, or 0 for webcam")
    parser.add_argument("--conf", type=float, default=0.35,
                        help="Confidence threshold (default: 0.35)")
    parser.add_argument("--model", type=str, default=None,
                        help="Path to model .pt file")
    parser.add_argument("--save-video", action="store_true",
                        help="Save annotated video to output/")
    args = parser.parse_args()

    # Find model
    model_path = args.model or find_model()
    if not model_path or not os.path.exists(model_path):
        print("  ❌ Model not found! Train first:  python train.py")
        sys.exit(1)

    print("=" * 50)
    print("  VAJRA-SHIELD — Drone Detection")
    print("=" * 50)
    print(f"  Model : {model_path}")
    print(f"  Source : {args.source}")
    print(f"  Conf   : {args.conf}")
    print("=" * 50)

    model = YOLO(model_path)

    source = args.source

    # Determine source type
    if source == "0" or source.isdigit():
        # Webcam
        detect_video(model, source, args.conf, save_output=False)
    elif os.path.isdir(source):
        # Folder of images
        exts = (".jpg", ".jpeg", ".png", ".bmp")
        imgs = [os.path.join(source, f) for f in os.listdir(source)
                if f.lower().endswith(exts)]
        print(f"  Found {len(imgs)} images in folder\n")
        for img_path in imgs:
            detect_image(model, img_path, args.conf)
    elif os.path.isfile(source):
        ext = os.path.splitext(source)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
            detect_image(model, source, args.conf)
        elif ext in (".mp4", ".avi", ".mkv", ".mov", ".wmv"):
            detect_video(model, source, args.conf, save_output=args.save_video)
        else:
            print(f"  ❌ Unsupported file type: {ext}")
    else:
        print(f"  ❌ Source not found: {source}")


if __name__ == "__main__":
    main()
