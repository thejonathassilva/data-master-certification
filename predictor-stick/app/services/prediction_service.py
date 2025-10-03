from typing import Dict, Any, List, Tuple, Optional
import concurrent.futures, time
from bson import ObjectId
from app.core.config import settings
from app.infrastructure.cache import model_cache
from app.repositories.channels_repo import ChannelsRepository
from app.repositories.subjects_repo import SubjectsRepository
from app.repositories.intents_repository import IntentsRepository
from app.repositories.mongo_reference_repository import MongoReferenceRepository
from app.services.minio_storage_service import MinioStorageService
from app.domain.dtos import EntityDTO, PredictionResponse
from app.utils.preprocess_text import preprocess_text

import logging
log = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.channels_repo = ChannelsRepository()
        self.subjects_repo = SubjectsRepository()
        self.intents_repo = IntentsRepository()
        self.reference_repo = MongoReferenceRepository()
        self.storage = MinioStorageService()

    # --- Prediction flow ---
    def predict(self, channel_name: str, text: str) -> PredictionResponse:
        channel_id = self.channels_repo.get_by_name(channel_name)
        subjects = self.subjects_repo.list_by_channel(channel_id["_id"])

        log.info("Found %d", len(subjects))

        bests = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(predict_subject, subject, text, self.reference_repo, self.storage): subject for subject in subjects
            }

            for future in concurrent.futures.as_completed(futures):
                log.info("Processing future...")
                try:
                    result = future.result()
                    if result:
                        bests.append(result)
                        print("Prediction added")
                except Exception as e:
                    log.error("Error to process prediction")

        if not bests:
            log.warn("No prediction met the confidence threshold")
            return None
        
        subject, text, intent, confidence = max(bests, key=lambda x: x[3])
        log.info("Best prediction: Subject id %s. IntentId %s. Confidence %s", 
                 subject['_id'], intent, confidence)
        

        return {
            "subjectId": subject['_id'],
            "intentName": intent,
            "confidence": confidence
        }
    

def predict_subject(subject, text, reference_repo, storage):
        clean_text = preprocess_text(text)
        tokens = clean_text.split()

        try:
            vectorizer_ref = reference_repo.load_j_assistant_reference(subject["_id"], "vectorizer")
            print(vectorizer_ref)
            start = time.perf_counter()

            vectorizer = storage.load_from_minio_url(vectorizer_ref["minio_url"])

            end = time.perf_counter()
            print(f"Vectorizer loaded in {end - start:.2f} seconds for subject {subject['_id']}")

            if vectorizer.vocabulary_ is None:
                print(f"Vectorizer vocabulary is None for subject {subject['_id']}. Skipping prediction.")
                return None
            
            if not any(token in vectorizer.vocabulary_ for token in tokens):
                print(f"No tokens found in vectorizer vocabulary for subject{subject['_id']}. Skipping prediction")
                return None
            
            print(f"Predicting for subject {subject['_id']} ({subject['name']}) with text: {clean_text}")

            clf_ref = reference_repo.load_j_assistant_reference(subject["_id"], "clf")
            start = time.perf_counter()
            
            clf = storage.load_from_minio_url(clf_ref["minio_url"])
                      
            end = time.perf_counter()
            print(f"Classifier loaded in {end - start:.2f} seconds for subject {subject['_id']}")

        except ValueError as e:
            print(f"Model not found for subject {subject['_id']}: {e}")
            return None
        
        text_vectorized = vectorizer.transform([clean_text])
        prediction = clf.predict(text_vectorized)[0]
        confidence = clf.predict_proba(text_vectorized).max()

        print(f"Prediction for subject {subject['_id']} ({subject['name']}): {prediction} with confidence {confidence:.4}")
        return (subject, text, prediction, confidence)