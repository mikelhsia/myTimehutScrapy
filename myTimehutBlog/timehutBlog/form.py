from django import forms
from .models import PeekabooCollectionComment, Profile
from django.contrib.auth.models import User

# Remember that Django has two base classes to build forms: Form and ModelForm.

# Used the first one previously to let your users share posts by e-mail.
class EmailCollectionForm(forms.Form):
	# This type of field is rendered as an <input type="text"> HTML element.
	name = forms.CharField(max_length=25)
	email = forms.EmailField()
	to = forms.EmailField()
	# In the comments field, we use a Textarea widget to display it as a <textarea> HTML element
	# instead of the default <input> element.
	comments = forms.CharField(required=True, widget=forms.Textarea)


# In the this case, you will need to use ModelForm because you have to build a form dynamically from your Comment model.
class CommentForm(forms.ModelForm):
	class Meta:
		# Django introspects the model and builds the form dynamically for us
		model = PeekabooCollectionComment
		fields = ('name', 'email', 'body')


# Log-in view form
class LoginForm(forms.Form):
	username = forms.CharField()
	# PasswordInput widget to render its HTML input element, including type='password' attribute
	password = forms.CharField(widget=forms.PasswordInput)

# User registration
class UserRegistrationForm(forms.ModelForm):
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'email')

		def clean_password2(self):
			cd = self.clean_password2
			if cd['password'] != cd['password2']:
				raise forms.ValidationError('Passwords don\'t match.')

			return cd['password2']

class UserEditForm(forms.ModelForm):
	'''
	UserEditForm:
	Will allow users to edit their first name, last name, and e-mail, which are stored in the built-in User model
	'''
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
	'''
	ProfileEditForm:
	Will allow users to edit the extra data we save in the custom Profile model.
	Users will be able to edit their date of birth and upload a picture for their profile.
	'''
	class Meta:
		model = Profile
		fields = ('date_of_birth', 'photo')