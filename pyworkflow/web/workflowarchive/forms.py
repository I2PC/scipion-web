from django import forms
from workflowarchive.models import Workflow

#The basic idea is to create two forms; one with the FileField and the other
# form with the document, description, ... fields.
#The user views the form with FileField first. Once the user uploads the file
# and submits the request, I call the other form with initial values read
# from the file (I can also delete the file at this step).

class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow

class FileUploadForm(forms.Form):

    workflowName = forms.CharField(max_length=128, required=True)
    description = forms.CharField(widget=forms.Textarea(), max_length= 512)
    file = forms.FileField(label='Attach workflow file')

    data_dict={}

    def clean_workflowName(self):
        self.data_dict['name'] = self.cleaned_data["workflowName"]

    def clean_description(self):
        self.data_dict['description'] = self.cleaned_data["description"]

    def clean_file(self):
        data = self.cleaned_data["file"]
        # read and parse the file, create a Python dictionary `data_dict` from it

        self.data_dict['content'] = data.read()

        form = WorkflowForm(self.data_dict)
        if form.is_valid():
            # we don't want to put the object to the database on this step
            #do I need to save this?
            self.instance = form.save(commit=False)
        else:
            # You can use more specific error message here
            raise forms.ValidationError(form.errors)
        return data

    def save(self):
        # We are not overriding the `save` method here because `form.Form` does not have it.
        # We just add it for convenience.
        print "SSSSSAVE"
        instance = getattr(self, "instance", None)
        if instance:
            print "save instance"
            instance.save()
        return instance
        #fields = ('description', 'document', )

    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row = u'<p%(html_class_attr)s>%(label)s</p> &nbsp;&nbsp;%(field)s%(help_text)s<p>&nbsp;</p>',
            error_row = u'%s',
            row_ender = '</p>',
            help_text_html = u' <span class="helptext">%s</span>',
            errors_on_separate_row = True)