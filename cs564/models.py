from django.db import models
from django.core.urlresolvers import reverse


class ObservationPath(models.Model):
    """
    obs path model represents one or more coordinates from which PV array is viewed.
    Goal is to check these points against array for glare.
    """
    name = models.CharField(help_text='Name of observation', max_length=30)
    direction = models.DecimalField(help_text='direction (if flight path)',
            max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class SunPath(models.Model):
    """
    Sun path is entire trajectory of sun movement across sky, for one year.
    lat/lng represents observatoin point from which we view sun.
    """
    observer_lat = models.DecimalField(help_text='Observer latitude',
            max_digits=7, decimal_places=5)
    observer_lng = models.DecimalField(help_text='Observer longitude',
            max_digits=8, decimal_places=5)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        # This is how Django handles composite primary keys
        unique_together = (("observer_lat", "observer_lng"),)


class SunPosition(models.Model):
    """
    Single location of sun at given time.
    """
    dt = models.DateTimeField()
    sun_path = models.ForeignKey(SunPath, on_delete=models.CASCADE)
    azimuth = models.DecimalField(max_digits=6, decimal_places=3)
    elevation = models.DecimalField(max_digits=5, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = (("dt", "sun_path"),)


class Panel(models.Model):
    """
    PV arrays are comprised of panels.
    """
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    reflectivity = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    index_of_refrac = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = (("name", "manufacturer"),)


class PVArray(models.Model):
    """
    Photovoltaic array installation.
    We want to know if these cause glare when viewed from observer position.
    """
    name = models.CharField(max_length=100)
    orientation = models.DecimalField(max_digits=6, decimal_places=3, default=180)
    tilt = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    height = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    panel = models.ForeignKey(Panel, help_text='Type of panel', null=True,
            on_delete=models.SET_NULL)
    sun_path = models.ForeignKey(SunPath, blank=True, null=True,
            on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Coordinate(models.Model):
    """
    Generic latitude/longitude coordinate.
    Used by observation to designate place from which we view PV array.
    Also used by PV array to designate vertices of array footprint.
    """
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    elevation = models.DecimalField(help_text='Ground elevation (m)', max_digits=10, decimal_places=2)
    height = models.DecimalField(help_text='Height above ground (m)', max_digits=10, decimal_places=2, default=0)
    path = models.ForeignKey(ObservationPath, null=True, blank=True,
            on_delete=models.CASCADE)
    pv_array = models.ForeignKey(PVArray, null=True, blank=True,
            on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = (
                ("latitude", "longitude", "height", "path"),
                ("latitude", "longitude", "height", "pv_array"),
                )

    def get_absolute_url(self):
        return reverse('coordinate_detail', kwargs={'pk': self.pk})


class Analysis(models.Model):
    """
    An analysis represents computation of specified arrays and observations,
    and whether or not glare is present.
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class AnalysisComponent(models.Model):
    """
    Use component to add array or obs path to given analysis.
    """
    analysis = models.ForeignKey(Analysis,
            on_delete=models.CASCADE)
    path = models.ForeignKey(ObservationPath, null=True, blank=True,
            on_delete=models.SET_NULL)
    pv_array = models.ForeignKey(PVArray, null=True, blank=True,
            on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = (
                ('analysis', 'path', 'pv_array'),
                )




