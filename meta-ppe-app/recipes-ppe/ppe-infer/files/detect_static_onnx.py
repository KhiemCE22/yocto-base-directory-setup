#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, os, json, time
from datetime import datetime
import numpy as np
import cv2  
import onnxruntime as ort

# ---------- Utils ----------
def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True):
    shape = img.shape[:2]  # h, w
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:
        r = min(r, 1.0)
    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    if auto:
        dw, dh = np.mod(dw, 32), np.mod(dh, 32)
    elif scaleFill:
        new_unpad = (new_shape[1], new_shape[0])
        dw, dh = 0, 0
        r = (new_shape[1] / shape[1], new_shape[0] / shape[0])
    top, bottom = int(round(dh/2 - 0.1)), int(round(dh/2 + 0.1))
    left, right  = int(round(dw/2 - 0.1)), int(round(dw/2 + 0.1))
    img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, r, (left, top)

def nms_boxes(boxes, scores, iou_thr=0.45):
    idxs = scores.argsort()[::-1]
    keep = []
    while idxs.size:
        i = idxs[0]
        keep.append(i)
        if idxs.size == 1: break
        xx1 = np.maximum(boxes[i,0], boxes[idxs[1:],0])
        yy1 = np.maximum(boxes[i,1], boxes[idxs[1:],1])
        xx2 = np.minimum(boxes[i,2], boxes[idxs[1:],2])
        yy2 = np.minimum(boxes[i,3], boxes[idxs[1:],3])
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        area_i = (boxes[i,2]-boxes[i,0])*(boxes[i,3]-boxes[i,1])
        area_r = (boxes[idxs[1:],2]-boxes[idxs[1:],0])*(boxes[idxs[1:],3]-boxes[idxs[1:],1])
        iou = inter / (area_i + area_r - inter + 1e-7)
        idxs = idxs[1:][iou <= iou_thr]
    return np.array(keep, dtype=int)

def scale_coords(box_xywh, gain, pad):
    # xywh (letterboxed) -> xyxy (original image)
    cx, cy, w, h = box_xywh.T
    cx = (cx - pad[0]) / gain
    cy = (cy - pad[1]) / gain
    w  = w / gain
    h  = h / gain
    x1 = cx - w/2; y1 = cy - h/2
    x2 = cx + w/2; y2 = cy + h/2
    return np.stack([x1, y1, x2, y2], axis=1)

def pick_providers(force_cpu=False):
    if force_cpu:
        return ["CPUExecutionProvider"]
    available = ort.get_available_providers()
    return (["CUDAExecutionProvider", "CPUExecutionProvider"]
            if "CUDAExecutionProvider" in available else ["CPUExecutionProvider"])

def load_class_names(classes_path=None, pt_path=None):
    names = None
    # optional: lấy từ .pt nếu muốn (cần ultralytics, không khuyến khích trên Yocto)
    if pt_path and os.path.exists(pt_path):
        try:
            from ultralytics import YOLO
            m = YOLO(pt_path)
            raw = m.names
            names = [raw[i] for i in sorted(raw.keys())] if isinstance(raw, dict) else list(raw)
        except Exception:
            names = None
    if names is None and classes_path and os.path.exists(classes_path):
        with open(classes_path, "r", encoding="utf-8") as f:
            names = [ln.strip() for ln in f if ln.strip()]
    return names  # có thể None

def standardize_yolo_onnx_output(out0, class_names, img_size=640):
    preds = out0
    if preds.ndim == 3 and preds.shape[0] == 1:
        C, K = preds.shape[1], preds.shape[2]
        preds = np.transpose(preds, (0, 2, 1))[0] if (C <= 305 and K > C) else preds[0]
    elif preds.ndim == 2:
        pass
    else:
        raise RuntimeError(f"Unsupported ONNX output shape: {preds.shape}")

    C = preds.shape[1]
    if C < 6:
        raise RuntimeError(f"Unexpected channel dim C={C} (<6)")

    has_obj, nc = None, None
    if class_names:
        if C == 4 + len(class_names):
            has_obj, nc = False, len(class_names)
        elif C == 5 + len(class_names):
            has_obj, nc = True, len(class_names)
    if has_obj is None:
        nc_noobj, nc_withobj = C - 4, C - 5
        if nc_noobj >= 1 and (nc_withobj < 1 or nc_noobj <= 300):
            has_obj, nc = False, nc_noobj
        else:
            has_obj, nc = True, nc_withobj

    boxes_xywh = preds[:, :4].astype(np.float32)
    if has_obj:
        obj_conf   = preds[:, 4:5].astype(np.float32)
        cls_scores = preds[:, 5:5+nc].astype(np.float32)
    else:
        obj_conf   = np.ones((preds.shape[0], 1), dtype=np.float32)
        cls_scores = preds[:, 4:4+nc].astype(np.float32)

    def needs_sigmoid(a):
        return (np.nanmax(a) > 1.0) or (np.nanmin(a) < 0.0)
    if needs_sigmoid(obj_conf):   obj_conf = 1.0 / (1.0 + np.exp(-obj_conf))
    if needs_sigmoid(cls_scores): cls_scores = 1.0 / (1.0 + np.exp(-cls_scores))

    if (class_names is None) or (len(class_names) != nc):
        class_names = [f"class_{i}" for i in range(nc)]

    cls_ids  = np.argmax(cls_scores, axis=1)
    cls_conf = cls_scores[np.arange(cls_scores.shape[0]), cls_ids]
    conf     = (obj_conf[:, 0] * cls_conf).astype(np.float32)

    mxy = float(np.nanmax(boxes_xywh[:, :2])) if boxes_xywh.size else 0.0
    mwh = float(np.nanmax(boxes_xywh[:, 2:4])) if boxes_xywh.size else 0.0
    if mxy <= 1.5 and mwh <= 1.5:
        boxes_xywh = boxes_xywh * float(img_size)
    already_in_orig = (mxy > img_size + 2 or mwh > img_size + 2)

    return boxes_xywh, conf, cls_ids, class_names, already_in_orig

def run_once(model_path, image_path, out_path, log_path, classes_path=None, pt_path=None,
             img_size=640, conf_thres=0.25, iou_thres=0.45, force_cpu=False):
    class_names = load_class_names(classes_path, pt_path)
    orig = cv2.imread(image_path)
    assert orig is not None, f"Không đọc được ảnh: {image_path}"
    ih, iw = orig.shape[:2]

    img, gain, pad = letterbox(orig, (img_size, img_size), auto=False)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    img_chw = np.transpose(img_rgb, (2,0,1))[None, ...]

    providers = pick_providers(force_cpu)
    sess = ort.InferenceSession(model_path, providers=providers)
    in_name = sess.get_inputs()[0].name

    t0 = time.time()
    out = sess.run(None, {in_name: img_chw})
    infer_ms = (time.time() - t0) * 1000.0

    preds0 = out[0]
    boxes_xywh, conf, cls_ids, class_names, already_in_orig = standardize_yolo_onnx_output(
        preds0, class_names, img_size=img_size
    )

    # filter conf
    mask = conf >= conf_thres
    boxes_xywh = boxes_xywh[mask]
    conf = conf[mask]
    cls_ids = cls_ids[mask]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    annotated = orig.copy()

    if boxes_xywh.size == 0:
        cv2.imwrite(out_path, annotated)
        event = {
            "time": datetime.now().isoformat(),
            "image": os.path.abspath(image_path),
            "output_image": os.path.abspath(out_path),
            "infer_ms": round(infer_ms, 2),
            "detections": []
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    if already_in_orig:
        cx, cy, w, h = boxes_xywh.T
        x1 = cx - w/2; y1 = cy - h/2; x2 = cx + w/2; y2 = cy + h/2
        boxes_xyxy = np.stack([x1,y1,x2,y2], axis=1)
    else:
        boxes_xyxy = scale_coords(boxes_xywh, gain, pad)

    final = []
    for c in np.unique(cls_ids):
        idxs = np.where(cls_ids == c)[0]
        keep = nms_boxes(boxes_xyxy[idxs], conf[idxs], iou_thr=iou_thres)
        for j in idxs[keep]:
            final.append((j, int(c)))

    dets_json = []
    for j, c in final:
        x1,y1,x2,y2 = boxes_xyxy[j].tolist()
        score = float(conf[j])
        name = class_names[c] if c < len(class_names) else f"class_{c}"
        x1 = int(max(0, x1)); y1 = int(max(0, y1))
        x2 = int(min(iw-1, x2)); y2 = int(min(ih-1, y2))
        cv2.rectangle(annotated, (x1,y1), (x2,y2), (0,255,0), 2)
        label = f"{name} {score:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, y1- th - 6), (x1 + tw + 2, y1), (0,255,0), -1)
        cv2.putText(annotated, label, (x1+1, y1-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

        dets_json.append({
            "class_id": int(c),
            "class_name": name,
            "confidence": round(score, 4),
            "bbox_xyxy": [x1, y1, x2, y2]
        })

    cv2.imwrite(out_path, annotated)
    event = {
        "time": datetime.now().isoformat(),
        "image": os.path.abspath(image_path),
        "output_image": os.path.abspath(out_path),
        "infer_ms": round(infer_ms, 2),
        "detections": dets_json
    }
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event

def parse_args():
    ap = argparse.ArgumentParser(description="Static image detection with ONNX (YOLOv5/YOLOv8 style)")
    ap.add_argument("--model", default="/opt/models/ppe_model.onnx", help="Đường dẫn model .onnx")
    ap.add_argument("--image", required=True, help="Ảnh đầu vào (đường dẫn file)")
    ap.add_argument("--out",   default="/var/lib/ppe/annotated.jpg", help="Ảnh output có bbox")
    ap.add_argument("--log",   default="/var/log/ppe/detections.jsonl", help="File JSONL log")
    ap.add_argument("--classes", default="/opt/models/classes.txt", help="File tên lớp (mỗi dòng 1 tên)")
    ap.add_argument("--imgsz", type=int, default=640, help="Kích thước input (vuông)")
    ap.add_argument("--conf",  type=float, default=0.25, help="Ngưỡng confidence")
    ap.add_argument("--iou",   type=float, default=0.45, help="Ngưỡng IoU NMS")
    ap.add_argument("--cpu",   action="store_true", help="Chỉ dùng CPUExecutionProvider")
    ap.add_argument("--pt",    default=None, help="Tùy chọn: .pt để lấy class names (không khuyến nghị trên Yocto)")
    return ap.parse_args()

def main():
    args = parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    os.makedirs(os.path.dirname(args.log), exist_ok=True)
    event = run_once(
        model_path=args.model,
        image_path=args.image,
        out_path=args.out,
        log_path=args.log,
        classes_path=args.classes,
        pt_path=args.pt,
        img_size=args.imgsz,
        conf_thres=args.conf,
        iou_thres=args.iou,
        force_cpu=args.cpu
    )
    print(json.dumps(event, ensure_ascii=False))

if __name__ == "__main__":
    main()
