
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from cs564.models import ObservationPath, Coordinate, Panel, PVArray, Analysis, AnalysisComponent
from cs564.forms import ObservationPathForm, CoordinateForm, PanelForm, PVArrayForm, AnalysisForm, ComponentForm


####################
## ANALYSIS VIEWS ##

@login_required
def analysis_list(request):
    """
    Display list of all analyses, if request is GET.
    If request is POST, user is submitting new analysis.
    Add it to DB and display page.
    """
    analysis_list = Analysis.objects.all().order_by('-created_at')[:30]
    if request.method == "POST":
    	a_form = AnalysisForm(request.POST)
        if a_form.is_valid():
            # save new analysis to DB
            analysis = a_form.save()
        else:
            # if submission fails validation, user will see errors.
            pass
    else:
    	a_form = AnalysisForm()
    # data used to fill out HTML template for display.
    context = {
            'analysis_list': analysis_list,
            'a_form': a_form,
            }
    return render(request, 'cs564/analysis_list.html', context)


@login_required
def analysis_detail(request, pk=None):
    """
    Loads when user clicks on analysis id for detailed view.
    Also redirected here when analysis is updated OR component added to it.
    """
    analysis = get_object_or_404(Analysis, pk=pk)
    pv_array_list = PVArray.objects.all()
    op_list = ObservationPath.objects.all()
    # get all PV array components for this analysis, using JOIN and conditions
    array_component_list = AnalysisComponent.objects.filter(
                    analysis=analysis.id
            ).filter(
                    path__isnull=True
            )
    a_array_list = [component.pv_array for component in array_component_list]
    # get all obs path components for this analysis, using JOIN and conditions
    path_component_list = AnalysisComponent.objects.filter(
                    analysis=analysis.id
            ).filter(
                    pv_array__isnull=True
            )
    a_op_list = [component.path for component in path_component_list]

    if request.method == "POST":
        # user is trying to update analysis data
        a_form = AnalysisForm(request.POST, instance=analysis)
        if a_form.is_valid():
            a_form.save()  # updates existing analysis
        else:
            pass
    else:
        a_form = AnalysisForm()

    component_form = ComponentForm()
    context = {
            'a_form': a_form,
            'component_form': component_form,
            'analysis': analysis,
            'pv_array_list': pv_array_list,
            'op_list': op_list,
            'a_array_list': a_array_list,
            'a_op_list': a_op_list,
            }
    return render(request, 'cs564/analysis_detail.html', context)


@login_required
def analysis_delete(request, pk):
    """
    Delete the analysis and relevant AnalysisComponents.
    Then display analysis list page.
    """
    if request.method == "POST":
        analysis = Analysis.objects.get(pk=pk)
        analysis.delete()
    request.method = "GET"
    return analysis_list(request)


@login_required
def analysis_component_add(request, analysis_id):
    """
    When user selects PV array or obs path in analysis detail page, add it as component.
    """
    if request.method == "POST":
        comp_array_form = ComponentForm(request.POST, prefix='array')
        comp_op_form = ComponentForm(request.POST, prefix='op')
        if comp_array_form.is_valid():
            pv_array = comp_array_form.save()
        if comp_op_form.is_valid():
            op = comp_op_form.save()
    # redirect to redisplay detail page
    request.method = "GET"
    return analysis_detail(request, analysis_id)


@login_required
def analysis_array_remove(request, analysis_id, pv_array_id):
    """
    User removes PV array as component of analysis
    """
    if request.method == "POST":
        # find DB object and delete it
        component = AnalysisComponent.objects.get(analysis=analysis_id, pv_array=pv_array_id)
        component.delete()
        request.method = "GET"
        return analysis_detail(request, analysis_id)

@login_required
def analysis_op_remove(request, analysis_id, op_id):
    """
    User removes obs path as component of analysis
    """
    if request.method == "POST":
        # find DB object and delete it
        component = AnalysisComponent.objects.get(analysis=analysis_id, path=op_id)
        component.delete()
        request.method = "GET"
        return analysis_detail(request, analysis_id)



################################
###    Observation Paths #######

@login_required
def observation_path_list(request):
    """
    Show observation paths.
    If POST, user is trying to create new path.
    """
    if request.method == "POST":
    	op_form = ObservationPathForm(request.POST)
        if op_form.is_valid():
            op = op_form.save()
        else:
            pass
    else:
        op_form = ObservationPathForm()
    op_list = ObservationPath.objects.all().order_by('-created_at')[:30]
    context = {
            'op_form': op_form,
            'op_list': op_list,
            }
    return render(request, 'cs564/observationpath_list.html', context)


@login_required
def observation_path_delete(request, pk):
    """
    Delete the observation path, all associated coordinates.
    Then display the obs path list.
    """
    if request.method == "POST":
        op = ObservationPath.objects.get(pk=pk)
        coord_list = Coordinate.objects.filter(path=pk)
        coord_list.delete()
        op.delete()
    request.method = "GET"
    return observation_path_list(request)
    return redirect('/cs564/op/')


@login_required
def observation_path_detail(request, pk=None):
    """
    Loads when user clicks on obs path for detailed view.
    Also redirected here when obs path is updated OR coordinate added to it.
    """
    op = get_object_or_404(ObservationPath, pk=pk)
    if request.method == "POST":
    	  # determine which form submitted
        attrs = request.POST.keys()
        if 'direction' in attrs:
        	  # obs path form submitted to update path
            op_form = ObservationPathForm(request.POST, instance=op)
            coord_form = CoordinateForm()
            if op_form.is_valid():
                op_form.save()
            # return to templ and show errors so don't change coord_form
            else:
                pass

        # coordinate form submitted for new coordinate
        elif 'c-elevation' in attrs:
            op_form = ObservationPathForm()
            coord_form = CoordinateForm(request.POST, prefix="c")
            if coord_form.is_valid():
                coord = coord_form.save()
            else: 
                pass
        else:
            raise Http404
    else:
        op_form = ObservationPathForm()
        coord_form = CoordinateForm()

    coord_list = Coordinate.objects.filter(path=pk)
    context = {
            'op': op,
            'p_form': op_form,
            'c_form': coord_form,
            'coord_list': coord_list
            }
    return render(request, 'cs564/observationpath_detail.html', context)


@login_required
def observation_path_coordinate_delete(request, op_id, coord_id):
    """
    User clicks "delete" to remove coordinate from this obs path
    """
    op = get_object_or_404(ObservationPath, pk=op_id)
    if request.method == "POST":
    	coord = Coordinate.objects.get(pk=coord_id)
    	coord.delete()

    request.method = "GET"
    return redirect('/cs564/op/' + op_id)



###################################
####    PANELS    ################

@login_required
def panel_list(request):
    """
    Show panels.
    If POST, user is trying to create new panel.
    """
    if request.method == "POST":
    	panel_form = PanelForm(request.POST)
        if panel_form.is_valid():
            panel = panel_form.save()
        else:
            pass
    else:
    	panel_form = PanelForm()
    panel_list = Panel.objects.all().order_by('-created_at')[:30]
    context = {
            'panel_form': panel_form,
            'panel_list': panel_list,
            }
    return render(request, 'cs564/panel_list.html', context)


@login_required
def panel_delete(request, pk):
    """
    Delete the panel.
    Then display the panel list.
    """
    if request.method == "POST":
    	panel = Panel.objects.get(pk=pk)
    	panel.delete()
    request.method = "GET"
    return panel_list(request)
    return redirect('/cs564/panel/')



###################################
######      PV ARRAYS       ######

@login_required
def pv_array_list(request):
    """
    Show arrays.
    If POST, user is trying to create new pv array.
    """
    #import pdb; pdb.set_trace()
    if request.method == "POST":
    	pv_array_form = PVArrayForm(request.POST)
        if pv_array_form.is_valid():
            pv_array = pv_array_form.save()  # add to DB if valid submission
        else:
            pass
    else:
    	pv_array_form = PVArrayForm()
    pv_array_list = PVArray.objects.all().order_by('-created_at')[:30]
    panel_list = Panel.objects.all()
    context = {
            'pv_array_form': pv_array_form,
            'pv_array_list': pv_array_list,
            'panel_list': panel_list,
            }
    return render(request, 'cs564/pvarray_list.html', context)


@login_required
def pv_array_delete(request, pk):
    """
    Delete the pv array clicked, and all associated coordinates.
    Then display the array list.
    """
    if request.method == "POST":
    	pv_array = PVArray.objects.get(pk=pk)
    	# grab all coordinates attached to this array
    	coord_list = Coordinate.objects.filter(path=pk)
    	coord_list.delete()
        if pv_array.sun_path:
            pv_array.sun_path.delete()
    	pv_array.delete()
    request.method = "GET"
    return pv_array_list(request)
    return redirect('/cs564/pv_array/')


@login_required
def pv_array_detail(request, pk=None):
    """
    Loads when user clicks on PV array for detailed view.
    Also redirected here when PV array is updated OR coordinate added to it.
    """
    pv_array = get_object_or_404(PVArray, pk=pk)
    if request.method == "POST":
    	# determine which form submitted.
    	# User is either updating PV array data or is adding new Coordinate.
        attrs = request.POST.keys()
        if 'tilt' in attrs:
        	# array form submitted to update array
            pv_array_form = PVArrayForm(request.POST, instance=pv_array)
            coord_form = CoordinateForm()
            if pv_array_form.is_valid():
            	# update pv_array
            	pv_array_form.save()
            else:
            	# return to templ and show errors so don't change coord_form
            	pass

        elif 'c-elevation' in attrs:
            # coordinate form submitted for new coordinate
            pv_array_form = PVArrayForm()
            coord_form = CoordinateForm(request.POST, prefix="c")
            if coord_form.is_valid():
                coord = coord_form.save()
            else:
            	# return to templ and show errors so don't change pv_array_form
            	pass
        else:
        	raise Http404
    else:
    	pv_array_form = PVArrayForm()
    	coord_form = CoordinateForm()

    coord_list = Coordinate.objects.filter(pv_array_id=pk)
    panel_list = Panel.objects.all().order_by('-created_at')[:30]
    context = {
            'pv_array': pv_array,
            'p_form': pv_array_form,
            'c_form': coord_form,
            'coord_list': coord_list,
            'panel_list': panel_list,
            }
    return render(request, 'cs564/pvarray_detail.html', context)


@login_required
def pv_array_coordinate_delete(request, pv_array_id, coord_id):
    """
    User clicked "delete" on a coordinate.
    Delete coordinate, removing it from PV array.
    """
    pv_array = get_object_or_404(PVArray, pk=pv_array_id)
    if request.method == "POST":
    	coord = Coordinate.objects.get(pk=coord_id)
    	coord.delete()

    request.method = "GET"
    return redirect('/cs564/pv_array/' + pv_array_id)


