from django import forms
from .models import Study, Analysis, Participants, Results

class StudyForm(forms.ModelForm):

    class Meta:
        model = Study
        fields = ('author', 'consortium', 'pmid', 'publication_date', 'trait', 'efo', 'analysis', 'source')

class AnalysisForm(forms.ModelForm):

    class Meta:
        model = Analysis
        fields = ('outcome', 'exposure', 'covariates', 'outcome_unit', 'exposure_unit', 'array', 'tissue', 'further_details')

class ParticipantsForm(forms.ModelForm):

    class Meta:
        model = Participants
        fields = ('n', 'n_studies', 'categories', 'age', 'n_males', 'n_females', 'n_eur', 'n_eas', 'n_sas', 'n_afr', 'n_amr', 'n_oth')

class ResultsForm(forms.ModelForm):

    class Meta:
        model = Results
        fields = ('cpg', 'beta', 'se', 'p', 'i2', 'p_het', 'details')

class UploadFileForm(forms.Form):
    file = forms.FileField(" ")
