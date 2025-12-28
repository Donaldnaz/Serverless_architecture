import os 
import json
import time
import re
import spacy
import multiprocessing
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage
from google.auth import default
from langdetect import detect, detect_langs, DetectorFactory
from cloudevents.http import CloudEvent
import functions_framework
from google.auth.transport.requests import Request

# === Global Setup ===
DetectorFactory.seed = 0
storage_client = storage.Client()
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# === Model Configuration ===
MODEL_BUCKET = os.environ.get("MODEL_BUCKET", "your-model-bucket")
MODEL_PATH = os.environ.get("MODEL_PATH", "models/deepseek-base")
LOCAL_MODEL_DIR = "/tmp/deepseek-model"

# === Output Configuration ===
INPUT_PREFIX = os.environ.get("INPUT_PREFIX", "uploads/")
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "translations/")
OUTPUT_BUCKET_NAME = os.environ.get("OUTPUT_BUCKET", "your-output-bucket")

SUPPORTED_LANGS = {
    "en": "English",
    "ar": "Arabic",
    "ja": "Japanese"
}

# === Model Loading ===
def download_model_from_gcs():
    """Download model from GCS to local storage"""
    if os.path.exists(LOCAL_MODEL_DIR):
        print(f"[INFO] Model already exists at {LOCAL_MODEL_DIR}")
        return LOCAL_MODEL_DIR
    
    os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
    
    bucket = storage_client.bucket(MODEL_BUCKET)
    blobs = bucket.list_blobs(prefix=MODEL_PATH)
    
    for blob in blobs:
        # Create relative path
        relative_path = blob.name[len(MODEL_PATH)+1:] if len(blob.name) > len(MODEL_PATH) else ""
        local_path = os.path.join(LOCAL_MODEL_DIR, relative_path)
        
        # Create directories if needed
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download file
        print(f"[INFO] Downloading {blob.name} to {local_path}")
        blob.download_to_filename(local_path)
    
    print(f"[INFO] Model downloaded to {LOCAL_MODEL_DIR}")
    return LOCAL_MODEL_DIR

def load_model():
    """Load the model from local directory"""
    # Import transformers here to avoid loading at startup if not needed
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    
    model_dir = download_model_from_gcs()
    
    print("[INFO] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    
    print("[INFO] Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        device_map="auto",  # Will use GPU if available
        torch_dtype="auto",
        low_cpu_mem_usage=True
    )
    
    print("[INFO] Creating pipeline...")
    translator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1
    )
    
    return translator

# Initialize model globally (but loaded lazily)
_model = None

def get_model():
    """Get or initialize the model singleton"""
    global _model
    if _model is None:
        _model = load_model()
    return _model

# === Utilities ===
def split_into_sentences(text):
    return [sent.text.strip() for sent in nlp(text).sents]

def remove_english(text: str) -> str:
    cleaned = re.sub(r"[A-Za-z0-9:?\n]+", "", text)
    return cleaned.strip()

def clean_output(raw_output):
    # Extract translation from model output
    # This depends on your model's output format
    if isinstance(raw_output, list) and len(raw_output) > 0:
        raw_output = raw_output[0].get('generated_text', '')
    
    # Try to extract just the translated part
    # Adjust this based on your model's actual output format
    lines = raw_output.split('\n')
    for line in lines:
        if 'Translation:' in line:
            return line.split('Translation:')[1].strip()
    
    # Fallback: return last line or whole output
    return lines[-1] if lines else raw_output.strip()

def call_local_translation(text, target_lang):
    """Call the locally loaded model for translation"""
    prompt = f"Translate the following English text into {target_lang}:\n\n{text}\n\nTranslation:"
    
    try:
        model = get_model()
        result = model(
            prompt,
            max_new_tokens=512,
            temperature=0.15,
            do_sample=True,
            top_p=0.95,
            num_return_sequences=1
        )
        
        print(f"[DEBUG] Raw model output: {result}")
        return clean_output(result)
    
    except Exception as e:
        print(f"[ERROR] Model inference failed: {e}")
        # Fallback to simple response
        return f"[Translated to {target_lang}]: {text}"

def parse_srt_blocks(srt_text: str):
    pattern = re.compile(
        r'(\d+)\s*\n'
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*'
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*\n'
        r'(?P<text>(?:.+(?:\n(?!\d+\n).+)*)?)'
        r'(?:\n{2,}|\Z)',
        re.DOTALL
    )
    blocks = []
    srt_text = srt_text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n\n"
    for m in pattern.finditer(srt_text):
        idx = m.group(1)
        start = m.group(2)
        end = m.group(3)
        text = (m.group('text') or "").rstrip("\n")
        lines = text.split("\n") if text else [""]
        blocks.append({"index": idx, "timestamp": f"{start} --> {end}", "lines": lines})
    return blocks

def reconstruct_srt(blocks):
    out = []
    for b in blocks:
        out.append(str(b["index"]))
        out.append(b["timestamp"])
        out.extend(b["lines"] if b["lines"] else [""])
        out.append("")
    return "\n".join(out)

# === TXT Translation ===
def translate_txt_to_all_languages(text):
    try:
        src_lang = detect(text[:500])
    except:
        src_lang = "unknown"

    print(f"[INFO] Detected source language: {SUPPORTED_LANGS.get(src_lang, src_lang)}")
    
    sentences = split_into_sentences(text)
    chunks = []
    for sentence in sentences:
        words = sentence.strip().split()
        if len(words) <= 10:
            chunks.append(sentence)
        else:
            for i in range(0, len(words), 10):
                chunks.append(" ".join(words[i:i+10]))

    output = {}
    
    for code, lang in SUPPORTED_LANGS.items():
        if code == src_lang:
            continue
        
        translated = [''] * len(chunks)
        
        def worker(i, chunk):
            try:
                translated_text = call_local_translation(chunk, lang)
                print(f"[DEBUG] ({lang}) Chunk {i}: {translated_text}")
                return i, remove_english(translated_text)
            except Exception as e:
                print(f"[ERROR] Translation failed for chunk {i}: {e}")
                return i, "[Translation Failed]"
        
        with ThreadPoolExecutor(max_workers=max(8, multiprocessing.cpu_count()*2)) as executor:
            futures = [executor.submit(worker, i, chunk) for i, chunk in enumerate(chunks)]
            for f in as_completed(futures):
                i, t = f.result()
                translated[i] = t
        
        output[lang] = " ".join(translated)

    return output, src_lang

# === SRT Translation ===
def translate_srt_to_all_languages(srt_text):
    blocks = parse_srt_blocks(srt_text)
    joined_text = " ".join([b['text'] for b in blocks])

    try:
        src_lang = detect(joined_text[:500])
    except:
        print("[WARN] Falling back to English.")
        src_lang = "en"

    print(f"[INFO] Detected source language: {SUPPORTED_LANGS.get(src_lang, src_lang)}")
    output = {}

    for code, lang in SUPPORTED_LANGS.items():
        if code == src_lang:
            continue

        translated_blocks = [''] * len(blocks)

        def worker(i, block):
            chunks = []
            for sent in split_into_sentences(block["text"]):
                words = sent.strip().split()
                if len(words) <= 10:
                    chunks.append(sent)
                else:
                    for j in range(0, len(words), 10):
                        chunks.append(" ".join(words[j:j+10]))

            translated = []
            for chunk in chunks:
                try:
                    translated_text = call_local_translation(chunk, lang)
                    translated.append(remove_english(translated_text))
                except Exception as e:
                    print(f"[ERROR] Translation failed: {e}")
                    translated.append("[Translation Failed]")

            return i, {"index": block["index"], "timestamp": block["timestamp"], "text": " ".join(translated)}

        with ThreadPoolExecutor(max_workers=max(8, multiprocessing.cpu_count()*2)) as executor:
            futures = [executor.submit(worker, i, b) for i, b in enumerate(blocks)]
            for f in as_completed(futures):
                i, translated_block = f.result()
                translated_blocks[i] = translated_block

        output[lang] = reconstruct_srt(translated_blocks)
    
    return output, src_lang

# === JSON Translation ===
def translate_JSON_to_all_languages(json_text):
    blocks = process_JSON_input(json_text)
    joined_text = " ".join([b['text'] for b in blocks if 'text' in b])

    try:
        src_lang = detect(joined_text[:500])
    except:
        print("[WARN] Falling back to English.")
        src_lang = "en"

    print(f"[INFO] Detected source language: {SUPPORTED_LANGS.get(src_lang, src_lang)}")
    output = {}

    for code, lang in SUPPORTED_LANGS.items():
        if code == src_lang:
            continue

        translated_blocks = [''] * len(blocks)

        def worker(i, block):
            chunks = []
            for sent in split_into_sentences(block.get("text", "")):
                words = sent.strip().split()
                if len(words) <= 10:
                    chunks.append(sent)
                else:
                    for j in range(0, len(words), 10):
                        chunks.append(" ".join(words[j:j+10]))

            translated = []
            for chunk in chunks:
                try:
                    translated_text = call_local_translation(chunk, lang)
                    translated.append(remove_english(translated_text))
                except Exception as e:
                    print(f"[ERROR] Translation failed: {e}")
                    translated.append("[Translation Failed]")

            return i, {
                "timestamp": block.get("timestamp", ""),
                "text": " ".join(translated),
                "speaker": block.get("speaker", ""),
                "flagged": block.get("flagged", False)
            }

        with ThreadPoolExecutor(max_workers=max(8, multiprocessing.cpu_count() * 2)) as executor:
            futures = [executor.submit(worker, i, b) for i, b in enumerate(blocks)]
            for f in as_completed(futures):
                i, translated_block = f.result()
                translated_blocks[i] = translated_block

        output[lang] = translated_blocks

    return output, src_lang

def process_JSON_input(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        print("[ERROR] Could not decode JSON.")
        return []

def reconstruct_json(blocks):
    return [
        {
            "timestamp": b['timestamp'],
            "text": b['text'],
            "speaker": b['speaker'],
            "flagged": b.get('flagged', False)
        }
        for b in blocks
    ]

@functions_framework.cloud_event
def translate_on_upload(cloud_event: CloudEvent):
    start = time.time()
    data = cloud_event.data
    file_name = data["name"]
    bucket_name = data["bucket"]

    if not file_name.startswith(INPUT_PREFIX):
        print(f"[SKIP] Not in input folder: {file_name}")
        return
    if not (file_name.endswith(".srt") or file_name.endswith(".txt") or file_name.endswith(".json")):
        print(f"[SKIP] Unsupported file type: {file_name}")
        return
    
    base_name = os.path.basename(file_name)
    input_blob = storage_client.bucket(bucket_name).blob(file_name)
    process_blob = storage_client.bucket(bucket_name).blob(f"{file_name}.processing")
    done_blob = storage_client.bucket(bucket_name).blob(f"{file_name}.done")
    output_bucket = storage_client.bucket(OUTPUT_BUCKET_NAME)

    if done_blob.exists():
        print("[SKIP] Already done.")
        return
    if process_blob.exists():
        print("[SKIP] Already processing.")
        return

    process_blob.upload_from_string("processing", content_type="text/plain")
    content = input_blob.download_as_text(encoding="utf-8")

    try:
        if file_name.endswith(".srt"):
            translated_data, src_lang = translate_srt_to_all_languages(content)
            output_dir = f"{OUTPUT_PREFIX}srt_outputs"
            file_type = "srt"
        elif file_name.endswith(".txt"):
            translated_data, src_lang = translate_txt_to_all_languages(content)
            output_dir = f"{OUTPUT_PREFIX}text_outputs"
            file_type = "txt"
        elif file_name.endswith(".json"):
            translated_data, src_lang = translate_JSON_to_all_languages(content)
            output_dir = f"{OUTPUT_PREFIX}json_outputs"
            file_type = "json"
        else:
            print(f"[SKIP] Unsupported extension.")
            return
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        process_blob.delete()  # Clean up processing flag on error
        return

    for lang, translated_text in translated_data.items():
        output_path = f"{output_dir}/{lang.lower()}_{base_name}"
        output_blob = output_bucket.blob(output_path)
        if file_type == "json":
            output_blob.upload_from_string(
                json.dumps(translated_text, indent=4),
                content_type="application/json; charset=utf-8"
            )
        else:
            output_blob.upload_from_string(
                translated_text,
                content_type="text/plain; charset=utf-8"
            )
        print(f"[✅] Uploaded: {output_path}")

    # Cleanup
    for blob in output_bucket.list_blobs(prefix=output_dir + "/"):
        if blob.name.endswith(".done") or blob.name.endswith(".processing"):
            print(f"[🧹] Deleting stray file: {blob.name}")
            blob.delete()

    process_blob.delete()  # Remove processing flag
    done_blob.upload_from_string("done", content_type="text/plain")
    print(f"[ DONE] Elapsed time: {time.time() - start:.2f}s")
