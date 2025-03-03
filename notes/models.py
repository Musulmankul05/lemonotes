from users.models import UserModel
from django.db import models
from uuid import uuid4

from cryptography.fernet import Fernet

from lemonotes.settings import ENCRYPT_KEY


class TagModel(models.Model):
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=100, unique=True)


class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    private = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(default=uuid4, editable=False, unique=True)
    tags = models.ManyToManyField(TagModel, blank=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    fernet = Fernet(ENCRYPT_KEY)

    def __str__(self):
        return f'{self.user}: {self.title}'

    def encrypt_text(self, plaintext):
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt_text(self, ciphertext):
        return self.fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def encrypt_text_static(plaintext):
        return Fernet(ENCRYPT_KEY).encrypt(plaintext.encode()).decode()

    @staticmethod
    def decrypt_text_static(ciphertext):
        return Fernet(ENCRYPT_KEY).decrypt(ciphertext.encode()).decode()

    def check_password(self, raw_password):
        return raw_password == self.password

    def set_password(self, raw_password):
        self.password = raw_password
        self.save()

    def save(self, *args, **kwargs):
        # Decrypt title and content if they are already encrypted
        if self.pk:  # Check if the object already exists
            try:
                self.title = self.decrypt_text(self.title)
            except Exception:
                pass  # If decryption fails, it means the title is already plaintext or not set

            try:
                self.content = self.decrypt_text(self.content)
            except Exception:
                pass  # If decryption fails, it means the content is already plaintext or not set

        # Encrypt the title and content before saving
        if self.title:
            self.title = self.encrypt_text(self.title)
        if self.content:
            self.content = self.encrypt_text(self.content)

        super().save(*args, **kwargs)

    def decrypted_content(self):
        return self.decrypt_text(self.content)

    def decrypted_title(self):
        return self.decrypt_text(self.title)
