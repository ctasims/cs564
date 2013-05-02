from django.forms import ModelForm
from cs564 import models


class ObservationPathForm(ModelForm):
    class Meta:
        model = models.ObservationPath

class PanelForm(ModelForm):
    class Meta:
        model = models.Panel

class CoordinateForm(ModelForm):
    class Meta:
        model = models.Coordinate

class PVArrayForm(ModelForm):
    class Meta:
        model = models.PVArray

class AnalysisForm(ModelForm):
    class Meta:
        model = models.Analysis

class ComponentForm(ModelForm):
    class Meta:
        model = models.AnalysisComponent
