"""Bhashini ULCA client wrapper with resilient fallbacks."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

import config


@dataclass
class BhashiniClient:
    """Client for ASR/TTS/NMT using ULCA config + inference pipeline."""

    auth_url: str = config.BHASHINI_API_URL
    inference_url: str = config.BHASHINI_INFERENCE_URL
    ulca_api_key: str = config.BHASHINI_API_KEY
    user_id: str = config.BHASHINI_USER_ID
    timeout_seconds: int = 20
    _service_cache: Optional[Dict] = None

    def _demo_asr_text(self, language: str) -> str:
        if language == "hi":
            return "मेरा उद्यम नंबर UDYAM-RJ-01-0012345 है और खरीदार का नाम XYZ Engineering है"
        return "My Udyam number is UDYAM-RJ-01-0012345 and buyer name is XYZ Engineering"

    def _resolve_pipeline_config(self, task_type: str, source_language: str, target_language: Optional[str] = None) -> Dict:
        """Get ULCA pipeline service config and inference auth details."""
        cache_key = f"{task_type}:{source_language}:{target_language or ''}"
        if self._service_cache and cache_key in self._service_cache:
            return self._service_cache[cache_key]

        payload: Dict = {
            "pipelineTasks": [
                {
                    "taskType": task_type,
                    "config": {"language": {"sourceLanguage": source_language}},
                }
            ]
        }
        if target_language:
            payload["pipelineTasks"][0]["config"]["language"]["targetLanguage"] = target_language

        headers = {
            "userID": self.user_id,
            "ulcaApiKey": self.ulca_api_key,
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.auth_url}/ulca/apis/v0/model/getModelsPipeline", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return {}

        service_id = ""
        pipeline_cfg = data.get("pipelineResponseConfig", [])
        if pipeline_cfg and isinstance(pipeline_cfg, list):
            cfg_entries = pipeline_cfg[0].get("config", [])
            if cfg_entries and isinstance(cfg_entries, list):
                service_id = cfg_entries[0].get("serviceId", "")

        endpoint_cfg = data.get("pipelineInferenceAPIEndPoint", {}) or {}
        callback_url = endpoint_cfg.get("callbackUrl") or self.inference_url
        inference_key = endpoint_cfg.get("inferenceApiKey", {}) or {}
        api_key = inference_key.get("value", "")
        name = inference_key.get("name", "Authorization")

        resolved = {
            "serviceId": service_id,
            "callbackUrl": callback_url,
            "api_header_name": name,
            "api_header_value": api_key,
        }
        if self._service_cache is None:
            self._service_cache = {}
        self._service_cache[cache_key] = resolved
        return resolved

    def speech_to_text(self, audio_base64: str, language: str = "hi") -> Dict:
        """Transcribe speech payload using Bhashini ASR pipeline."""
        if config.APP_MODE == "DEMO":
            return {"text": self._demo_asr_text(language), "raw": {}, "source": "demo"}

        cfg = self._resolve_pipeline_config("asr", language)
        if not cfg.get("serviceId"):
            return {"text": "", "raw": {}, "source": "fallback"}
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": language},
                        "serviceId": cfg["serviceId"],
                    },
                }
            ],
            "inputData": {"audio": [{"audioContent": audio_base64}]},
        }
        headers = {"Content-Type": "application/json"}
        if cfg.get("api_header_value"):
            header_name = cfg.get("api_header_name", "Authorization")
            value = cfg["api_header_value"]
            headers[header_name] = value
            if header_name.lower() != "authorization":
                headers["Authorization"] = f"Bearer {value}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(cfg.get("callbackUrl") or f"{self.inference_url}/services/inference/pipeline", json=payload, headers=headers)
                if response.is_success:
                    data = response.json()
                    outputs = data.get("pipelineResponse", [])
                    if outputs and isinstance(outputs, list):
                        first = outputs[0].get("output", [{}])
                        if first and isinstance(first, list):
                            text = first[0].get("source", "")
                            if text:
                                return {"text": text, "raw": data, "source": "bhashini"}
        except Exception:
            pass
        return {"text": "", "raw": {}, "source": "fallback"}

    def text_to_speech(self, text: str, language: str = "hi", gender: str = "female") -> Dict:
        """Convert text to speech using Bhashini TTS pipeline."""
        if config.APP_MODE == "DEMO":
            return {"audio": base64.b64encode(text.encode("utf-8")).decode("utf-8"), "raw": {}, "source": "demo"}

        cfg = self._resolve_pipeline_config("tts", language)
        if not cfg.get("serviceId"):
            return {"audio": "", "raw": {}, "source": "fallback"}
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {"sourceLanguage": language},
                        "gender": gender,
                        "serviceId": cfg["serviceId"],
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        headers = {"Content-Type": "application/json"}
        if cfg.get("api_header_value"):
            header_name = cfg.get("api_header_name", "Authorization")
            value = cfg["api_header_value"]
            headers[header_name] = value
            if header_name.lower() != "authorization":
                headers["Authorization"] = f"Bearer {value}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(cfg.get("callbackUrl") or f"{self.inference_url}/services/inference/pipeline", json=payload, headers=headers)
                if response.is_success:
                    data = response.json()
                    outputs = data.get("pipelineResponse", [])
                    if outputs and isinstance(outputs, list):
                        first = outputs[0].get("audio", [{}])
                        if first and isinstance(first, list):
                            audio = first[0].get("audioContent", "")
                            if audio:
                                return {"audio": audio, "raw": data, "source": "bhashini"}
        except Exception:
            pass
        return {"audio": "", "raw": {}, "source": "fallback"}

    def translate(self, text: str, source_language: str = "hi", target_language: str = "en") -> Dict:
        """Translate text between supported languages."""
        if source_language == target_language:
            return {"text": text, "raw": {}, "source": "same_language"}
        if config.APP_MODE == "DEMO":
            return {"text": text, "raw": {}, "source": "demo"}

        cfg = self._resolve_pipeline_config("translation", source_language, target_language=target_language)
        if not cfg.get("serviceId"):
            return {"text": text, "raw": {}, "source": "fallback"}
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {"sourceLanguage": source_language, "targetLanguage": target_language},
                        "serviceId": cfg["serviceId"],
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        headers = {"Content-Type": "application/json"}
        if cfg.get("api_header_value"):
            header_name = cfg.get("api_header_name", "Authorization")
            value = cfg["api_header_value"]
            headers[header_name] = value
            if header_name.lower() != "authorization":
                headers["Authorization"] = f"Bearer {value}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(cfg.get("callbackUrl") or f"{self.inference_url}/services/inference/pipeline", json=payload, headers=headers)
                if response.is_success:
                    data = response.json()
                    outputs = data.get("pipelineResponse", [])
                    if outputs and isinstance(outputs, list):
                        first = outputs[0].get("output", [{}])
                        if first and isinstance(first, list):
                            translated = first[0].get("target", "")
                            if translated:
                                return {"text": translated, "raw": data, "source": "bhashini"}
        except Exception:
            pass
        return {"text": text, "raw": {}, "source": "fallback"}

    def is_available(self) -> bool:
        """Basic reachability check for configured Bhashini host."""
        if config.APP_MODE == "DEMO":
            return True
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(self.auth_url)
                return response.status_code < 500
        except Exception:
            return False
