from huggingface_hub import hf_hub_download

from ultralytics import YOLO

from io import BytesIO

from transformers import (
    CLIPProcessor,
    CLIPModel
)

import torch
from PIL import Image


class VisionClient:

    def __init__(self):

        # ==========================================
        # 1. CARGAR MODELO YOLO
        # ==========================================

        model_path = hf_hub_download(
            repo_id="arunapb/yolo11l-food-segmentation",
            filename="best.pt"
        )

        self.yolo_model = YOLO(model_path)

        # ==========================================
        # 2. CARGAR CLIP
        # ==========================================

        modelo_clip = "openai/clip-vit-base-patch32"

        self.clip_processor = CLIPProcessor.from_pretrained(
            modelo_clip
        )

        self.clip_model = CLIPModel.from_pretrained(
            modelo_clip
        )

        # ==========================================
        # 3. CONFIGURAR DISPOSITIVO
        # ==========================================

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.clip_model.to(self.device)

        # ==========================================
        # 4. INGREDIENTES PARA CLIP
        # ==========================================

        self.ingredientes = [
            "arroz",
            "frijoles",
            "carne asada",
            "pollo",
            "zanahoria",
            "huevo",
            "lechuga",
            "tomate",
            "aguacate",
            "queso",
            "papas fritas",
            "kiwi"
        ]

        self.textos_busqueda = [
            f"una foto de {ingrediente}, comida"
            for ingrediente in self.ingredientes
        ]

    def analyze(self, image):

        # ==========================================
        # 1. ABRIR IMAGEN
        # ==========================================

        if isinstance(image, bytes):

            original_img = Image.open(
                BytesIO(image)
            ).convert("RGB")

        else:

            original_img = Image.open(
                image
            ).convert("RGB")

        print("====================================")
        print("IMAGEN:", original_img.size)
        print("DISPOSITIVO:", self.device)

        # ==========================================
        # 2. DETECCIÓN CON YOLO
        # ==========================================

        results = self.yolo_model.predict(
            source=original_img,
            conf=0.01,
            imgsz=640
        )

        result = results[0]

        numero_detecciones = (
            0
            if result.boxes is None
            else len(result.boxes)
        )

        print("YOLO DETECTÓ:", numero_detecciones, "objetos")

        # ==========================================
        # 3. RESULTADOS DE YOLO
        # ==========================================

        resultados_yolo = []

        if result.boxes is not None:

            cajas = result.boxes.xyxy.cpu().numpy()
            confianzas = result.boxes.conf.cpu().numpy()
            clases = result.boxes.cls.cpu().numpy()

            for i in range(len(cajas)):

                clase_id = int(clases[i])

                nombre_clase = self.yolo_model.names.get(
                    clase_id,
                    str(clase_id)
                )

                resultados_yolo.append({
                    "food": str(nombre_clase),
                    "confidence": round(
                        float(confianzas[i]),
                        4
                    ),
                    "class_id": clase_id,
                    "box": [
                        round(float(valor), 2)
                        for valor in cajas[i]
                    ]
                })

        print("RESULTADOS YOLO:")
        print(resultados_yolo)

        # ==========================================
        # SI YOLO NO DETECTÓ NADA
        # ==========================================

        if len(resultados_yolo) == 0:

            print("YOLO NO DETECTÓ OBJETOS")
            print("====================================")

            return {
                "success": True,
                "message": "YOLO no detectó alimentos",
                "yolo": [],
                "clip": [],
                "detections": []
            }

        # ==========================================
        # 4. OBTENER CAJAS
        # ==========================================

        cajas = result.boxes.xyxy.cpu().numpy()

        # ==========================================
        # 5. RECORTAR ALIMENTOS
        # ==========================================

        recortes = []

        for i, caja in enumerate(cajas):

            x_min, y_min, x_max, y_max = caja

            recorte = original_img.crop(
                (
                    int(x_min),
                    int(y_min),
                    int(x_max),
                    int(y_max)
                )
            )

            recortes.append(recorte)

        print("RECORTES CREADOS:", len(recortes))

        # ==========================================
        # 6. CLASIFICACIÓN CON CLIP
        # ==========================================

        resultados_clip = []

        for i, recorte in enumerate(recortes):

            inputs = self.clip_processor(
                text=self.textos_busqueda,
                images=recorte,
                return_tensors="pt",
                padding=True
            )

            inputs = {
                key: value.to(self.device)
                for key, value in inputs.items()
            }

            with torch.no_grad():

                outputs = self.clip_model(
                    **inputs
                )

            logits_per_image = outputs.logits_per_image

            probs = logits_per_image.softmax(
                dim=1
            )[0].cpu().numpy()

            # Obtener las 5 mejores opciones

            indices = probs.argsort()[-5:][::-1]

            top_5 = []

            for indice in indices:

                top_5.append({
                    "food": self.ingredientes[indice],
                    "confidence": round(
                        float(probs[indice]),
                        4
                    )
                })

            resultados_clip.append({
                "recorte": i + 1,
                "prediction": top_5[0],
                "top_5": top_5
            })

        print("====================================")
        print("RESULTADOS CLIP:")
        print(resultados_clip)

        # ==========================================
        # 7. RESPUESTA FINAL PARA PRUEBAS
        # ==========================================

        print("====================================")
        print("ANÁLISIS COMPLETO")
        print("====================================")

        return {
            "success": True,

            "image_size": {
                "width": original_img.width,
                "height": original_img.height
            },

            "yolo": resultados_yolo,

            "clip": resultados_clip,

            "detections": resultados_yolo
        }