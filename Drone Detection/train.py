# ============================================================
# VAJRA-SHIELD — TRAIN DRONE DETECTION MODEL
# ============================================================
# Run:  python train.py
# Time: ~2-4 hours on CPU (no GPU needed)
# Output: runs/vajra_v1/weights/best.pt
# ============================================================

from ultralytics import YOLO
import os
import yaml
import torch
import argparse

def main():
    parser = argparse.ArgumentParser(description="VAJRA-SHIELD — Train Drone Detection Model")
    default_device = "0" if torch.cuda.is_available() else "cpu"
    parser.add_argument("--device", type=str, default=default_device,
                        help=f"Device to train on (default: {default_device})")
    parser.add_argument("--epochs", type=int, default=30,
                        help="Number of epochs (default: 30)")
    parser.add_argument("--batch", type=int, default=16,
                        help="Batch size (default: 16)")
    parser.add_argument("--imgsz", type=int, default=416,
                        help="Image size (default: 416)")
    parser.add_argument("--workers", type=int, default=2,
                        help="Dataloader workers (default: 2)")
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="Base model weights (default: yolov8n.pt)")
    args = parser.parse_args()

    # ---- PATHS ----
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR = os.path.join(BASE_DIR, "Drone detection.v9i.yolov8")

    # Fix data.yaml with absolute paths (Roboflow's relative paths break locally)
    fixed_yaml = os.path.join(BASE_DIR, "data_local.yaml")

    config = {
        "train": os.path.join(DATASET_DIR, "train", "images"),
        "val":   os.path.join(DATASET_DIR, "valid", "images"),
        "test":  os.path.join(DATASET_DIR, "test",  "images"),
        "nc": 2,
        "names": ["bird", "drone"],
    }

    with open(fixed_yaml, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    device_label = f"GPU ({torch.cuda.get_device_name(0)})" if args.device != "cpu" and torch.cuda.is_available() else "CPU"

    print("=" * 55)
    print("  VAJRA-SHIELD — Drone Detection Training")
    print("=" * 55)
    print(f"  Dataset : {DATASET_DIR}")
    print(f"  Classes : bird (0), drone (1)")
    print(f"  Train   : {len(os.listdir(config['train']))} images")
    print(f"  Valid   : {len(os.listdir(config['val']))} images")
    print(f"  Config  : {fixed_yaml}")
    print(f"  Device  : {args.device} [{device_label}]")
    print(f"  Epochs  : {args.epochs} | Batch: {args.batch} | ImgSz: {args.imgsz} | Workers: {args.workers}")
    print("=" * 55)

    # ---- TRAIN ----
    model = YOLO(args.model)

    model.train(
        data=fixed_yaml,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=os.path.join(BASE_DIR, "runs"),
        name="vajra_v1",
        patience=15,
        save=True,
        plots=True,
        verbose=True,
        workers=args.workers,
        cache=False,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        fliplr=0.5,
        mosaic=1.0,
    )

    print("\n" + "=" * 55)
    print("  ✅ TRAINING DONE!")
    print("=" * 55)

    # ---- EVALUATE ON TEST SET ----
    best_pt = os.path.join(BASE_DIR, "runs", "vajra_v1", "weights", "best.pt")
    print(f"\n  Best model: {best_pt}")
    print(f"  Size: {os.path.getsize(best_pt) / (1024*1024):.1f} MB")

    print("\n  Running test evaluation...")
    model = YOLO(best_pt)
    metrics = model.val(data=fixed_yaml, split="test", device=args.device, verbose=True)

    print("\n" + "=" * 55)
    print("  📊 TEST RESULTS")
    print("=" * 55)
    print(f"  mAP@50     : {metrics.box.map50:.4f}")
    print(f"  mAP@50-95  : {metrics.box.map:.4f}")
    print(f"  Precision  : {metrics.box.mp:.4f}")
    print(f"  Recall     : {metrics.box.mr:.4f}")
    print("=" * 55)
    print(f"\n  Now run:  python detect.py --source your_video.mp4")

if __name__ == "__main__":
    main()

