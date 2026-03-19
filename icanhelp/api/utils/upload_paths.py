import os
import uuid
from rest_framework import serializers
from PIL import Image

def get_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join("images/avatars", f"{uuid.uuid4()}.{ext}")

def get_upload_category_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join("images/categories", f"{uuid.uuid4()}.{ext}")

def get_upload_competence_image__path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join("images/competences", f"{uuid.uuid4()}.{ext}")
