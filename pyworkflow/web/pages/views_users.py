from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from models import UserForm, UserProfileForm, UserProfile


class UserFormView(View):
    form_class = UserForm
    template_name = 'users/registration_form.html'

    # Display a blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # Process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            # Get an user object without saving to validate.
            user = form.save(commit=False)

            # Cleaned normalized data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # Return user objects if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')

        return render(request, self.template_name, {'form': form})


class UserProfileView(View):
    form_class = UserProfileForm
    template_name = 'users/user_profile_form.html'

    # Display a blank form
    def get(self, request):

        if request.user.is_authenticated():


            userprofile = request.user.userprofile

            form = self.form_class(instance=userprofile)
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('register')

    # Process form data
    def post(self, request):

        userprofile = request.user.userprofile

        form = self.form_class(request.POST, instance=userprofile)

        if form.is_valid() and request.user.is_authenticated():

            form.instance.user = request.user
            form.save()
            return redirect('home')

        return render(request, self.template_name, {'form': form})
