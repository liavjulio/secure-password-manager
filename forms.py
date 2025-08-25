"""
Web Forms for Secure Password Manager
Flask-WTF forms with validation for user input and CSRF protection.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from wtforms.widgets import PasswordInput
import re
from auth import is_password_strong, validate_username, validate_email
from models import get_user_by_username, get_user_by_email


class LoginForm(FlaskForm):
    """
    User login form with CSRF protection.
    
    Security Features:
    - CSRF token validation
    - Input length limits
    - Remember me functionality
    """
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required"),
            Length(min=3, max=30, message="Username must be 3-30 characters")
        ],
        render_kw={"placeholder": "Enter your username", "autocomplete": "username"}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required")
        ],
        render_kw={"placeholder": "Enter your password", "autocomplete": "current-password"}
    )
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """
    User registration form with comprehensive validation.
    
    Security Features:
    - Strong password requirements
    - Username uniqueness validation
    - Email format validation
    - Password confirmation
    - CSRF protection
    """
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required"),
            Length(min=3, max=30, message="Username must be 3-30 characters")
        ],
        render_kw={"placeholder": "Choose a username", "autocomplete": "username"}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email format"),
            Length(max=254, message="Email is too long")
        ],
        render_kw={"placeholder": "Enter your email", "autocomplete": "email"}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required"),
            Length(min=8, max=128, message="Password must be 8-128 characters")
        ],
        render_kw={"placeholder": "Create a strong password", "autocomplete": "new-password"}
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo('password', message="Passwords must match")
        ],
        render_kw={"placeholder": "Confirm your password", "autocomplete": "new-password"}
    )
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Custom validation for username requirements"""
        # Check username format
        is_valid, issues = validate_username(username.data)
        if not is_valid:
            raise ValidationError('; '.join(issues))
        
        # Check if username already exists
        if get_user_by_username(username.data):
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Custom validation for email requirements"""
        # Check email format
        is_valid, issues = validate_email(email.data)
        if not is_valid:
            raise ValidationError('; '.join(issues))
        
        # Check if email already exists
        if get_user_by_email(email.data):
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_password(self, password):
        """Custom validation for password strength"""
        is_strong, issues = is_password_strong(password.data)
        if not is_strong:
            raise ValidationError('; '.join(issues))


class PasswordForm(FlaskForm):
    """
    Password entry form for adding/editing stored passwords.
    
    Security Features:
    - Required field validation
    - URL format validation
    - Length limits for security
    - CSRF protection
    """
    
    service = StringField(
        'Service/Website',
        validators=[
            DataRequired(message="Service name is required"),
            Length(min=1, max=100, message="Service name must be 1-100 characters")
        ],
        render_kw={"placeholder": "e.g., Gmail, Facebook, Bank", "autocomplete": "off"}
    )
    
    username = StringField(
        'Username/Email',
        validators=[
            DataRequired(message="Username is required"),
            Length(min=1, max=100, message="Username must be 1-100 characters")
        ],
        render_kw={"placeholder": "Your username or email for this service", "autocomplete": "off"}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required"),
            Length(min=1, max=500, message="Password is too long")
        ],
        render_kw={"placeholder": "Password for this service", "autocomplete": "new-password"}
    )
    
    url = StringField(
        'Website URL',
        validators=[
            Optional(),
            Length(max=200, message="URL is too long")
        ],
        render_kw={"placeholder": "https://example.com (optional)", "autocomplete": "url"}
    )
    
    notes = TextAreaField(
        'Notes',
        validators=[
            Optional(),
            Length(max=1000, message="Notes are too long")
        ],
        render_kw={"placeholder": "Additional notes (optional)", "rows": 3}
    )
    
    submit = SubmitField('Save Password')
    
    def validate_url(self, url):
        """Custom validation for URL format"""
        if url.data:
            # Basic URL validation
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(url.data):
                raise ValidationError('Please enter a valid URL (e.g., https://example.com)')


class SearchForm(FlaskForm):
    """
    Search form for finding stored passwords.
    
    Features:
    - Text search across service, username, and URL
    - Optional field (can be empty)
    - CSRF protection
    """
    
    search_term = StringField(
        'Search',
        validators=[
            Optional(),
            Length(max=100, message="Search term is too long")
        ],
        render_kw={"placeholder": "Search passwords...", "autocomplete": "off"}
    )
    
    submit = SubmitField('Search')


class ChangePasswordForm(FlaskForm):
    """
    Form for changing user's master password.
    
    Security Features:
    - Current password verification
    - Strong password requirements
    - Password confirmation
    - CSRF protection
    """
    
    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message="Current password is required")
        ],
        render_kw={"placeholder": "Enter your current password", "autocomplete": "current-password"}
    )
    
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="New password is required"),
            Length(min=8, max=128, message="Password must be 8-128 characters")
        ],
        render_kw={"placeholder": "Enter your new password", "autocomplete": "new-password"}
    )
    
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message="Please confirm your new password"),
            EqualTo('new_password', message="Passwords must match")
        ],
        render_kw={"placeholder": "Confirm your new password", "autocomplete": "new-password"}
    )
    
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, new_password):
        """Custom validation for new password strength"""
        is_strong, issues = is_password_strong(new_password.data)
        if not is_strong:
            raise ValidationError('; '.join(issues))


class DeleteAccountForm(FlaskForm):
    """
    Form for account deletion with confirmation.
    
    Security Features:
    - Password confirmation required
    - Explicit confirmation checkbox
    - CSRF protection
    """
    
    password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Password confirmation is required")
        ],
        render_kw={"placeholder": "Enter your password to confirm", "autocomplete": "current-password"}
    )
    
    confirm_deletion = BooleanField(
        'I understand this action cannot be undone',
        validators=[
            DataRequired(message="You must confirm account deletion")
        ]
    )
    
    submit = SubmitField('Delete Account')


class PasswordGeneratorForm(FlaskForm):
    """
    Form for generating secure passwords.
    
    Features:
    - Customizable password length
    - Character set options
    - CSRF protection
    """
    
    length = StringField(
        'Password Length',
        validators=[
            DataRequired(message="Password length is required")
        ],
        default='16',
        render_kw={"type": "number", "min": "12", "max": "64", "step": "1"}
    )
    
    include_uppercase = BooleanField('Include Uppercase Letters', default=True)
    include_lowercase = BooleanField('Include Lowercase Letters', default=True)
    include_numbers = BooleanField('Include Numbers', default=True)
    include_symbols = BooleanField('Include Symbols', default=True)
    
    generate = SubmitField('Generate Password')
    
    def validate_length(self, length):
        """Validate password length"""
        try:
            length_int = int(length.data)
            if length_int < 12:
                raise ValidationError('Password length must be at least 12 characters')
            if length_int > 64:
                raise ValidationError('Password length cannot exceed 64 characters')
        except ValueError:
            raise ValidationError('Password length must be a number')
