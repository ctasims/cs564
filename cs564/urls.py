from django.conf.urls import patterns, url
from django.views.generic import TemplateView
#from django.views.generic import generic

from cs564.models import *

urlpatterns = patterns('cs564.views',
        # display index page when user navigates to ctasims.com/cs564
        url(r'^$',  
            TemplateView.as_view(template_name="cs564/index.html"),
            name="index"),

        ### ANALYSIS pages ###
        # matches url using regex, then loads specified view from views.py
        # each one has name, so we can use that shortcut in HTML instead of full
        # URL. 
        url(r'^analysis/$',
            'analysis_list',
            name="analysis_list"),
        url(r'^analysis/add$',
            'analysis_list',
            name="analysis_add"),
        url(r'^analysis/(?P<pk>\d+)/$',
            'analysis_detail',
            name="analysis_detail"),
        url(r'analysis/(?P<pk>\d+)/delete/$',
            'analysis_delete',
            name="analysis_delete"),

        url(r'analysis/(?P<analysis_id>\d+)/component/add/$',
            'analysis_component_add',
            name="analysis_component_add"),

        url(r'analysis/(?P<analysis_id>\d+)/array/(?P<pv_array_id>\d+)/remove/$',
            'analysis_array_remove',
            name="analysis_array_remove"),
        url(r'analysis/(?P<analysis_id>\d+)/op/(?P<op_id>\d+)/remove/$',
            'analysis_op_remove',
            name="analysis_op_remove"),


        #### OBS PATH URLS ###

        url(r'^op/$',
            'observation_path_list',
            name="op_list"),
        url(r'^op/add$',
            'observation_path_list',
            name="op_add"),
        url(r'op/(?P<pk>\d+)/delete/$',
            'observation_path_delete',
            name="op_delete"),

        url(r'^op/(?P<pk>\d+)/$',
            'observation_path_detail',
            name="op_detail"),
        url(r'^op/(?P<pk>\d+)/update/$',
            'observation_path_detail',
            name="op_update"),
        url(r'op/(?P<pk>\d+)/coordinate/add/$',
            'observation_path_detail',
            name="op_coord_add"),
        url(r'op/(?P<op_id>\d+)/coordinate/(?P<coord_id>\d+)/delete/$',
            'observation_path_coordinate_delete',
            name="op_coord_delete"),


        ##### PANELS #####

        url(r'^panel/$',
            'panel_list',
            name="panel_list"),
        url(r'^panel/add$',
            'panel_list',
            name="panel_add"),
        url(r'panel/(?P<pk>\d+)/delete/$',
            'panel_delete',
            name="panel_delete"),


        #### PV ARRAYS ###

        url(r'^pv_array/$',
            'pv_array_list',
            name="pv_array_list"),
        url(r'^pv_array/add$',
            'pv_array_list',
            name="pv_array_add"),
        url(r'pv_array/(?P<pk>\d+)/delete/$',
            'pv_array_delete',
            name="pv_array_delete"),

        url(r'^pv_array/(?P<pk>\d+)/$',
            'pv_array_detail',
            name="pv_array_detail"),
        url(r'^pv_array/(?P<pk>\d+)/update/$',
            'pv_array_detail',
            name="pv_array_update"),
        url(r'pv_array/(?P<pk>\d+)/coordinate/add/$',
            'pv_array_detail',
            name="pv_array_coord_add"),
        url(r'pv_array/(?P<pv_array_id>\d+)/coordinate/(?P<coord_id>\d+)/delete/$',
            'pv_array_coordinate_delete',
            name="pv_array_coord_delete"),
        )


         #### when user clicks Site Stats. link. ###
urlpatterns += patterns('cs564.queries',
        url(r'^queries/$',
            'query_list',
            name="query_list"),
        )
