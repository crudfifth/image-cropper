from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        errors = []
        if not 12 <= len(password) <= 16:
            errors.append('パスワードは12文字以上16文字以下である必要があります。')
        if not re.findall('[A-Z]', password):
            errors.append('パスワードには少なくとも1つの大文字が含まれている必要があります。')
        if not re.findall('[a-z]', password):
            errors.append('パスワードには少なくとも1つの小文字が含まれている必要があります。')
        if not re.findall('[0-9]', password):
            errors.append('パスワードには少なくとも1つの数字が含まれている必要があります。')
        if not re.findall(r'[@#$%^&*\-+_=\[\]{}|\\:\'?,/`~"();.]', password):
            errors.append('パスワードには少なくとも1つの記号が含まれている必要があります。')
        
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return 'パスワードは12文字以上16文字以下で、大文字、小文字、数字、記号を含む必要があります。'