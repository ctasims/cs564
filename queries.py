from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from cs564.models import ObservationPath, Coordinate, Panel, PVArray, Analysis, AnalysisComponent

import datetime


@login_required
def query_list(request):
    op_ct = ObservationPath.objects.count()
    coord_ct = Coordinate.objects.count()
    panel_ct = Panel.objects.count()
    array_ct = PVArray.objects.count()
    analysis_ct = Analysis.objects.count()
    counts = {
            'op': op_ct,
            'coord': coord_ct,
            'panel': panel_ct,
            'array': array_ct,
            'analysis': analysis_ct,
            }

    day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    op_recents = ObservationPath.objects.filter(created_at__gte=day_ago).count()
    coord_recents = Coordinate.objects.filter(created_at__gte=day_ago).count()
    panel_recents = Panel.objects.filter(created_at__gte=day_ago).count()
    array_recents = PVArray.objects.filter(created_at__gte=day_ago).count()
    analysis_recents = Analysis.objects.filter(created_at__gte=day_ago).count()
    recents = {
            'op': op_recents,
            'coord': coord_recents,
            'panel': panel_recents,
            'array': array_recents,
            'analysis': analysis_recents,
            }

    n_america_lats = [15, 75]
    n_america_lngs = [-120, -75]

    s_america_lats = [-60, 5]
    s_america_lngs = [-120, -75]

    europe_lats = [30, 60]
    europe_lngs = [-5, 45]

    asia_lats = [-10, 60]
    asia_lngs = [60, 180]

    africa_lats = [-30, 30]
    africa_lngs = [-15, 45]

    n_america_ops = ObservationPath.objects.filter(
                    coordinate__latitude__range=n_america_lats
            ).filter(
                    coordinate__longitude__range=n_america_lngs
            ).count()
    s_america_ops = ObservationPath.objects.filter(
                    coordinate__latitude__range=s_america_lats
            ).filter(
                    coordinate__longitude__range=s_america_lngs
            ).count()
    europe_ops = ObservationPath.objects.filter(
                    coordinate__latitude__range=europe_lats
            ).filter(
                    coordinate__longitude__range=europe_lngs
            ).count()
    asia_ops = ObservationPath.objects.filter(
                    coordinate__latitude__range=asia_lats
            ).filter(
                    coordinate__longitude__range=asia_lngs
            ).count()
    africa_ops = ObservationPath.objects.filter(
                    coordinate__latitude__range=africa_lats
            ).filter(
                    coordinate__longitude__range=africa_lngs
            ).count()

    n_america_arrays = PVArray.objects.filter(
                    coordinate__latitude__range=n_america_lats
            ).filter(
                    coordinate__longitude__range=n_america_lngs
            ).count()
    s_america_arrays = PVArray.objects.filter(
                    coordinate__latitude__range=s_america_lats
            ).filter(
                    coordinate__longitude__range=s_america_lngs
            ).count()
    europe_arrays = PVArray.objects.filter(
                    coordinate__latitude__range=europe_lats
            ).filter(
                    coordinate__longitude__range=europe_lngs
            ).count()
    asia_arrays = PVArray.objects.filter(
                    coordinate__latitude__range=asia_lats
            ).filter(
                    coordinate__longitude__range=asia_lngs
            ).count()
    africa_arrays = PVArray.objects.filter(
                    coordinate__latitude__range=africa_lats
            ).filter(
                    coordinate__longitude__range=africa_lngs
            ).count()

    geog_ops = {
            'n_america': n_america_ops,
            's_america': s_america_ops,
            'europe': europe_ops,
            'asia': asia_ops,
            'africa': africa_ops,
            }
    geog_arrays = {
            'n_america': n_america_arrays,
            's_america': s_america_arrays,
            'europe': europe_arrays,
            'asia': asia_arrays,
            'africa': africa_arrays,
            }



    context = {
            'counts': counts,
            'recents': recents,
            'geog_ops': geog_ops,
            'geog_arrays': geog_arrays,
            }

    return render(request, 'cs564/query_list.html', context)
